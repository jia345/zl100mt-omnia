/*
 * (C) Copyright 2013 Codethink Limited
 * Btrfs port to Uboot by
 * Adnan Ali <adnan.ali@codethink.co.uk>

 * btrfs.c -- readonly btrfs support for syslinux
 * Some data structures are derivated from btrfs-tools-0.19 ctree.h
 * Copyright 2009 Intel Corporation; author: alek.du@intel.com
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, Inc., 53 Temple Place Ste 330,
 * Boston MA 02111-1307, USA; either version 2 of the License, or
 * (at your option) any later version; incorporated herein by reference.
 *
 */

#include <malloc.h>
#include <common.h>
#include <btrfs.h>
#include <command.h>
#include <config.h>
#include <crc.h>
#include <fs.h>
#include <linux/compiler.h>
#include <linux/ctype.h>
#include <linux/stat.h>
#include <asm/byteorder.h>

unsigned long btr_part_offset;
static char crc_table_built;
/* Actual file structures (we don't have malloc yet...) */
struct file files[BTRFS_MAX_OPEN];
static u32 btrfs_crc32_table[256];
static block_dev_desc_t *btrfs_block_dev_desc;
static disk_partition_t *part_info;
struct inode parent_inode;

static void btrfs_init_crc32c(void)
{
	/* Bit-reflected CRC32C polynomial */
	crc32c_init(btrfs_crc32_table, 0x82F63B78);
}

static inline u32 crc32c_le(u32 crc, const char *data, size_t length)
{
	return crc32c_cal(crc, data, length, btrfs_crc32_table);
}

void btrfs_type(char num)
{
	switch (num) {
	case BTRFS_FILE:
		puts("<FILE>   "); break;
	case BTRFS_DIR:
		puts("<DIR>    "); break;
	case BTRFS_SYMLNK:
		puts("<SYM>    "); break;
	default:
		puts("<UNKNOWN>"); break;
	}
}

static inline __le32 next_psector(__le32 psector, uint32_t skip)
{
	if (EXTENT_SPECIAL(psector))
		return psector;
	else
		return psector + skip;
}

static inline __le32 next_pstart(const struct extent *e)
{
	return next_psector(e->pstart, e->len);
}

static inline struct inode *get_inode(struct inode *inode)
{
	inode->refcnt++;

	return inode;
}

/* compare function used for bin_search */
typedef int (*cmp_func)(const void *ptr1, const void *ptr2);

static int bin_search(void *ptr, int item_size, void *cmp_item, cmp_func func,
		      int min, int max, int *slot)
{
	int low = min;
	int high = max;
	int mid;
	int ret;
	unsigned long offset;
	void *item;

	while (low < high) {
		mid = (low + high) / 2;
		offset = mid * item_size;

		item = ptr + offset;
		ret = func(item, cmp_item);

		if (ret < 0)
			low = mid + 1;
		else if (ret > 0)
			high = mid;
		else {
			*slot = mid;
			return 0;
		}
	}
	*slot = low;

	return 1;
}

/* XXX: these should go into the filesystem instance structure */
static struct btrfs_chunk_map chunk_map;
static struct btrfs_super_block sb;
static u64 fs_tree;
/* compare btrfs chunk map in list*/
static int btrfs_comp_chunk_map(struct btrfs_chunk_map_item *m1,
				struct btrfs_chunk_map_item *m2)
{
	if (__le64_to_cpu(m1->logical) > __le64_to_cpu(m2->logical))
		return 1;

	if (__le64_to_cpu(m1->logical) < __le64_to_cpu(m2->logical))
		return -1;

	return 0;
}

/* insert a new chunk mapping item */
static void insert_chunk_item(struct btrfs_chunk_map_item *item)
{
	int ret;
	int slot;
	int i;

	if (chunk_map.map == NULL) { /* first item */
		chunk_map.map_length = BTRFS_MAX_CHUNK_ENTRIES;
		chunk_map.map = (struct btrfs_chunk_map_item *)
			malloc(chunk_map.map_length * sizeof(*chunk_map.map));
		chunk_map.map[0] = *item;
		chunk_map.cur_length = 1;

		return;
	}
	ret = bin_search(chunk_map.map, sizeof(*item), item,
				(cmp_func)btrfs_comp_chunk_map, 0,
				chunk_map.cur_length, &slot);
	if (ret == 0)/* already in map */
		return;

	if (chunk_map.cur_length == BTRFS_MAX_CHUNK_ENTRIES) {
		/* should be impossible */
		puts("too many chunk items\n");
		return;
	}
	for (i = chunk_map.cur_length; i > slot; i--)
		chunk_map.map[i] = chunk_map.map[i-1];
	chunk_map.map[slot] = *item;
	chunk_map.cur_length++;
}

static inline void insert_map(struct btrfs_disk_key *key,
				struct btrfs_chunk *chunk)
{
	struct btrfs_stripe *stripe = &chunk->stripe;
	struct btrfs_stripe *stripe_end = stripe + chunk->num_stripes;
	struct btrfs_chunk_map_item *item = malloc(sizeof(struct btrfs_chunk_map_item));

	item->logical = key->offset;
	item->length = chunk->length;
	for ( ; stripe < stripe_end; stripe++) {
		item->devid = stripe->devid;
		item->physical = stripe->offset;
		insert_chunk_item(item);
	}
}

/*
 * from sys_chunk_array or chunk_tree, we can convert a logical address to
 * a physical address we can not support multi device case yet
 */
static u64 logical_physical(u64 logical)
{
	struct btrfs_chunk_map_item item;
	int slot, ret;

	item.logical = logical;
	ret = bin_search(chunk_map.map, sizeof(*chunk_map.map), &item,
			(cmp_func)btrfs_comp_chunk_map, 0,
			chunk_map.cur_length, &slot);
	if (ret == 0)
		slot++;
	else if (slot == 0)
		return -1;

	if (logical >=
		chunk_map.map[slot-1].logical + chunk_map.map[slot-1].length)
		return -1;

	return chunk_map.map[slot-1].physical + logical -
			chunk_map.map[slot-1].logical;
}

/* static int btrfs_read(struct fs_info *fs, char *buf, u64 offset, u64 count)
devread(offset/BTRFS_SS, (offset%BTRFS_SS))
*/
int btrfs_devread(char *buf, u64 offset, u64 byte_len)
{
	ALLOC_CACHE_ALIGN_BUFFER(char, sec_buf, BTRFS_SS);
	unsigned block_len;
	u64 sector = (offset/BTRFS_SS);
	u64 byte_offset = (offset%BTRFS_SS);

	/* Get the read to the beginning of a partition */
	sector += byte_offset >> BTRFS_SECTOR_BITS;
	byte_offset &= BTRFS_SS - 1;

	if (btrfs_block_dev_desc == NULL) {
		puts("** Invalid Block Device Descriptor (NULL)\n");
		return 0;
	}
	if (byte_offset != 0) {
		/* read first part which isn't aligned with start of sector */
		if (btrfs_block_dev_desc->
				block_read(btrfs_block_dev_desc->dev,
					part_info->start + sector, 1,
					(unsigned long *) sec_buf) != 1) {
			puts(" ** btrfs_devread() read error **\n");
			return 0;
		}
		memcpy(buf, sec_buf + byte_offset,
			min(BTRFS_SS - byte_offset, byte_len));
		buf += min(BTRFS_SS - byte_offset, byte_len);
		byte_len -= min(BTRFS_SS - byte_offset, byte_len);
		sector++;
	}
	/* read sector aligned part */

	block_len = byte_len & ~(BTRFS_SS - 1);

	if (block_len == 0) {
		ALLOC_CACHE_ALIGN_BUFFER(u8, p, BTRFS_SS);

		block_len = BTRFS_SS;
		btrfs_block_dev_desc->block_read(btrfs_block_dev_desc->dev,
						part_info->start + sector,
						1, (unsigned long *)p);
		memcpy(buf, p, byte_len);
		return 1;
	}
	ALLOC_CACHE_ALIGN_BUFFER(u8, t, block_len);
	if (btrfs_block_dev_desc->block_read(btrfs_block_dev_desc->dev,
						part_info->start + sector,
						block_len / BTRFS_SS,
						(unsigned long *) t) !=
						block_len / BTRFS_SS) {
		debug(" ** %s read error - block\n", __func__);
		return 0;
	}

	memcpy(buf, t, block_len);
	block_len = byte_len & ~(BTRFS_SS - 1);
	buf += block_len;
	byte_len -= block_len;
	sector += block_len / BTRFS_SS;
	if (byte_len != 0) {
		/* read rest of data which are not in whole sector */
		if (btrfs_block_dev_desc->
			block_read(btrfs_block_dev_desc->dev,
				part_info->start + sector, 1,
				(unsigned long *) sec_buf) != 1) {
			debug("* %s read error - last part\n", __func__);
			return 0;
		}
		memcpy(buf, sec_buf, byte_len);
	}

	return 1;
}
/* btrfs has several super block mirrors, need to calculate their location */
static inline u64 btrfs_sb_offset(int mirror)
{
	u64 start = 16 * 1024;

	if (mirror)
		return start << (BTRFS_SUPER_MIRROR_SHIFT * mirror);

	return BTRFS_SUPER_INFO_OFFSET;
}

/* find the most recent super block */
static int btrfs_read_super_block(struct btrfs_info *fs)
{
	int i;
	u8 fsid[BTRFS_FSID_SIZE];
	u64 offset;
	u64 transid = 0;
	struct btrfs_super_block buf;

	sb.total_bytes = ~0;	/* Unknown as of yet */

	/*
	 * Only first header is checked for filesystem verification
	 * mirror of this header can be used if required
	 */
	/* find most recent super block */
	for (i = 0; i < BTRFS_SUPER_MIRROR_MAX; i++) {

		offset = btrfs_sb_offset(i);
		if (offset >= sb.total_bytes)
			break;

		if (btrfs_devread((char *)&buf, offset,
			sizeof(struct btrfs_super_block)) != 1)
			return -1;

		if (buf.bytenr != offset ||
				strncmp((char *)(&buf.magic),
				BTRFS_MAGIC, sizeof(buf.magic)))
			return -1;

		if (i == 0)
			memcpy(fsid, buf.fsid, sizeof(fsid));
		else if (memcmp(fsid, buf.fsid, sizeof(fsid))) {
			puts("fsid doesn't match\n");
			return -1;
		}

		if (buf.generation > transid) {
			memcpy(&sb, &buf, sizeof(sb));
			transid = buf.generation;
		}
	}

	return 0;
}

static inline unsigned long btrfs_chunk_item_size(int num_stripes)
{
	return sizeof(struct btrfs_chunk) +
		sizeof(struct btrfs_stripe) * (num_stripes - 1);
}

static void clear_path(struct btrfs_path *path)
{
	memset(path, 0, sizeof(*path));
}

static int btrfs_comp_keys(struct btrfs_disk_key *k1, struct btrfs_disk_key *k2)
{
	if (k1->objectid > k2->objectid)
		return 1;
	if (k1->objectid < k2->objectid)
		return -1;
	if (k1->type > k2->type)
		return 1;
	if (k1->type < k2->type)
		return -1;
	if (k1->offset > k2->offset)
		return 1;
	if (k1->offset < k2->offset)
		return -1;

	return 0;
}

/* compare keys but ignore offset, is useful to enumerate all same kind keys */
static int btrfs_comp_keys_type(struct btrfs_disk_key *k1,
					struct btrfs_disk_key *k2)
{
	if (k1->objectid > k2->objectid)
		return 1;
	if (k1->objectid < k2->objectid)
		return -1;
	if (k1->type > k2->type)
		return 1;
	if (k1->type < k2->type)
		return -1;

	return 0;
}

static union {
	struct btrfs_header header;
	struct btrfs_node node;
	struct btrfs_leaf leaf;
} *tree_buf;

/* seach tree directly on disk ... */
static int search_tree(struct btrfs_info *fs, u64 loffset,
		struct btrfs_disk_key *key, struct btrfs_path *path)
{
	int slot, ret;
	u64 offset;

	offset = logical_physical(loffset);
	btrfs_devread((char *)&tree_buf->header, offset, sizeof(tree_buf->header));
	if (tree_buf->header.level) {
		/* inner node */
		btrfs_devread((char *)&tree_buf->node.ptrs[0],
			   offset + sizeof tree_buf->header,
			   sb.nodesize - sizeof tree_buf->header);
		path->itemsnr[tree_buf->header.level] = tree_buf->header.nritems;
		path->offsets[tree_buf->header.level] = loffset;
		ret = bin_search(&tree_buf->node.ptrs[0],
				 sizeof(struct btrfs_key_ptr),
				 key, (cmp_func)btrfs_comp_keys,
				 path->slots[tree_buf->header.level],
				 tree_buf->header.nritems, &slot);
		if (ret && slot > path->slots[tree_buf->header.level])
			slot--;
		path->slots[tree_buf->header.level] = slot;
		ret = search_tree(fs, tree_buf->node.ptrs[slot].blockptr,
				  key, path);
	} else {
		/* leaf node */
		btrfs_devread((char *)&tree_buf->leaf.items[0],
			   offset + sizeof tree_buf->header,
			   sb.leafsize - sizeof tree_buf->header);
		path->itemsnr[tree_buf->header.level] = tree_buf->header.nritems;
		path->offsets[tree_buf->header.level] = loffset;
		ret = bin_search(&tree_buf->leaf.items[0],
				 sizeof(struct btrfs_item),
				 key, (cmp_func)btrfs_comp_keys,
				 path->slots[0],
				 tree_buf->header.nritems, &slot);
		if (ret && slot > path->slots[tree_buf->header.level])
			slot--;
		path->slots[tree_buf->header.level] = slot;
		path->item = tree_buf->leaf.items[slot];
		btrfs_devread((char *)&path->data,
			offset + sizeof tree_buf->header +
			tree_buf->leaf.items[slot].offset,
			tree_buf->leaf.items[slot].size);
	}

	return ret;
}

/* return 0 if leaf found */
static int next_leaf(struct btrfs_info *fs, struct btrfs_disk_key *key,
						struct btrfs_path *path)
{
	int slot;
	int level = 1;

	while (level < BTRFS_MAX_LEVEL) {
		if (!path->itemsnr[level]) /* no more nodes */
			return 1;

		slot = path->slots[level] + 1;
		if (slot >= path->itemsnr[level]) {
			level++;
			continue;
		}
		path->slots[level] = slot;
		path->slots[level-1] = 0; /* reset low level slots info */
		search_tree(fs, path->offsets[level], key, path);
		break;
	}
	if (level == BTRFS_MAX_LEVEL)
		return 1;

	return 0;
}

/* return 0 if slot found */
static int next_slot(struct btrfs_info *fs, struct btrfs_disk_key *key,
						struct btrfs_path *path)
{
	int slot;

	if (!path->itemsnr[0])
		return 1;

	slot = path->slots[0] + 1;
	if (slot >= path->itemsnr[0])
		return 1;

	path->slots[0] = slot;
	search_tree(fs, path->offsets[0], key, path);

	return 0;
}

/*
 * read chunk_array in super block
 */
static void btrfs_read_sys_chunk_array(void)
{
	struct btrfs_disk_key *key;
	struct btrfs_chunk *chunk;
	int cur;

	/* read chunk array in superblock */
	cur = 0;

	while (cur < __le32_to_cpu(sb.sys_chunk_array_size)) {
		key = (struct btrfs_disk_key *)(sb.sys_chunk_array + cur);
		cur += sizeof(*key);
		chunk = (struct btrfs_chunk *)(sb.sys_chunk_array + cur);
		cur += btrfs_chunk_item_size(chunk->num_stripes);
		insert_map(key, chunk);
	}
}

/* read chunk items from chunk_tree and insert them to chunk map */
static void btrfs_read_chunk_tree(struct btrfs_info *fs)
{
	struct btrfs_disk_key ignore_key;
	struct btrfs_disk_key search_key;
	struct btrfs_chunk *chunk;
	struct btrfs_path path;

	if (!(__le64_to_cpu(sb.flags) & BTRFS_SUPER_FLAG_METADUMP)) {
		if (__le64_to_cpu(sb.num_devices) > 1) {
			debug("warning: only support one btrfs device %lld\n",
				__le64_to_cpu(sb.num_devices));
			return;
		}
		ignore_key.objectid = BTRFS_DEV_ITEMS_OBJECTID;
		ignore_key.type = BTRFS_DEV_ITEM_KEY;

		/* read chunk from chunk_tree */
		search_key.objectid = BTRFS_FIRST_CHUNK_TREE_OBJECTID;
		search_key.type = BTRFS_CHUNK_ITEM_KEY;
		search_key.offset = 0;
		clear_path(&path);
		search_tree(fs, (sb.chunk_root), &search_key, &path);
		do {
			do {
				/* skip information about underlying block
				 * devices.
				 */
				if (!btrfs_comp_keys_type(&ignore_key,
							  &path.item.key))
					continue;
				if (btrfs_comp_keys_type(&search_key,
							&path.item.key))
					break;
				chunk = (struct btrfs_chunk *)(path.data);
				insert_map(&path.item.key, chunk);
			} while (!next_slot(fs, &search_key, &path));
			if (btrfs_comp_keys_type(&search_key, &path.item.key))
				break;
		} while (!next_leaf(fs, &search_key, &path));
	}
}

static inline u64 btrfs_name_hash(const char *name, int len)
{
	return btrfs_crc32c((u32)~1, name, len);
}

static struct inode *btrfs_iget_by_inr(struct btrfs_info *fs, u64 inr)
{
	struct inode *inode;
	struct btrfs_inode_item *inode_item;
	struct btrfs_disk_key search_key;
	struct btrfs_path path;
	struct btrfs_pvt_inode *pvt;
	int ret;

	/*
	*FIXME: some BTRFS inode member are u64, while our logical inode
	*is u32, we may need change them to u64 later
	*/
	search_key.objectid = inr;
	search_key.type = BTRFS_INODE_ITEM_KEY;
	search_key.offset = 0;
	clear_path(&path);
	ret = search_tree(fs, fs_tree, &search_key, &path);
	if (ret) {
		debug("%s search_tree failed\n", __func__);
		return NULL;
	}

	inode_item = (struct btrfs_inode_item *)path.data;
	inode = alloc_inode(fs, inr, sizeof(struct btrfs_pvt_inode));
	if (!(inode)) {
		debug("%s alloc_inode failed\n", __func__);
		return NULL;
	}

	inode->ino = inr;
	inode->size = inode_item->size;
	inode->mode = BTRFS_IFTODT(inode_item->mode);
	if (inode->mode == BTRFS_DT_REG || inode->mode == BTRFS_DT_LNK) {
		struct btrfs_file_extent_item *extent_item;
		u64 offset;

		/* get file_extent_item */
		search_key.type = BTRFS_EXTENT_DATA_KEY;
		search_key.offset = 0;
		clear_path(&path);
		ret = search_tree(fs, fs_tree, &search_key, &path);
		if (ret)
			return NULL; /* impossible */
		extent_item = (struct btrfs_file_extent_item *)path.data;
		if (extent_item->type == BTRFS_FILE_EXTENT_INLINE)
			offset = path.offsets[0] + sizeof(struct btrfs_header)
				+ path.item.offset
				+ offsetof(struct btrfs_file_extent_item,
								disk_bytenr);
		else
			offset = extent_item->disk_bytenr;
		pvt = (struct btrfs_pvt_inode *)inode->pvt;
		pvt->offset = offset;
	}

	return inode;
}

static struct inode *btrfs_iget_root(struct btrfs_info *fs)
{
	/* BTRFS_FIRST_CHUNK_TREE_OBJECTID(256) actually
	 * is first OBJECTID for FS_TREE
	 */
	return btrfs_iget_by_inr(fs, BTRFS_FIRST_CHUNK_TREE_OBJECTID);
}

static struct inode *btrfs_iget(const char *name, struct inode *parent)
{
	struct btrfs_info *fs = parent->fs;
	struct btrfs_disk_key search_key;
	struct btrfs_path path;
	struct btrfs_dir_item dir_item;
	int ret;

	search_key.objectid = parent->ino;
	search_key.type = BTRFS_DIR_ITEM_KEY;
	search_key.offset = btrfs_name_hash(name, strlen(name));
	clear_path(&path);
	ret = search_tree(fs, fs_tree, &search_key, &path);
	if (ret)
		return NULL;

	dir_item = *(struct btrfs_dir_item *)path.data;

	return btrfs_iget_by_inr(fs, dir_item.location.objectid);
}

static int btrfs_readlink(struct inode *inode, char *buf)
{
	struct btrfs_pvt_inode *pvt = (struct btrfs_pvt_inode *)inode->pvt;
	btrfs_devread((char *)buf, logical_physical(pvt->offset), inode->size);
	buf[inode->size] = '\0';
	return inode->size;
}

static int btrfs_readdir(struct file *file, struct btrfs_dirent *btrfs_dirent)
{
	struct btrfs_info *fs = file->fs;
	struct inode *inode = file->inode;
	struct btrfs_disk_key search_key;
	struct btrfs_path path;
	struct btrfs_dir_item *dir_item;
	int ret;

	/*
	 * we use file->offset to store last search key.offset, will will search
	 * key that lower that offset, 0 means first search and we will search
	 * -1UL, which is the biggest possible key
	 */
	search_key.objectid = inode->ino;
	search_key.type = BTRFS_DIR_ITEM_KEY;
	search_key.offset = file->offset - 1;
	clear_path(&path);
	ret = search_tree(fs, fs_tree, &search_key, &path);

	if (ret) {
		if (btrfs_comp_keys_type(&search_key, &path.item.key))
			return -1;
	}

	dir_item = (struct btrfs_dir_item *)path.data;
	file->offset = path.item.key.offset;
	btrfs_dirent->d_ino = dir_item->location.objectid;
	btrfs_dirent->d_off = file->offset;
	btrfs_dirent->d_reclen = offsetof(struct btrfs_dirent, d_name)
		+ dir_item->name_len + 1;
	btrfs_dirent->d_type = BTRFS_IFTODT(dir_item->type);
	memcpy(btrfs_dirent->d_name, dir_item + 1, dir_item->name_len);
	btrfs_dirent->d_name[dir_item->name_len] = '\0';
	btrfs_type(dir_item->type);
	printf("   %s\n", btrfs_dirent->d_name);

	return 0;
}

static int btrfs_next_extent(struct inode *inode, uint32_t lstart)
{
	struct btrfs_disk_key search_key;
	struct btrfs_file_extent_item *extent_item;
	struct btrfs_path path;
	int ret;
	u64 offset;
	struct btrfs_info *fs = inode->fs;
	struct btrfs_pvt_inode *pvt;
	u32 sec_shift = BTRFS_SECTOR_BITS;
	u32 sec_size = BTRFS_SS;

	search_key.objectid = inode->ino;
	search_key.type = BTRFS_EXTENT_DATA_KEY;
	search_key.offset = lstart << sec_shift;
	clear_path(&path);
	ret = search_tree(fs, fs_tree, &search_key, &path);
	if (ret) { /* impossible */
		puts("btrfs: search extent data error\n");
		return -1;
	}
	extent_item = (struct btrfs_file_extent_item *)path.data;

	if (extent_item->encryption) {
		puts("btrfs: found encrypted data, cannot continue\n");
		return -1;
	}
	if (extent_item->compression) {
		puts("btrfs: found compressed data, cannot continue\n");
		return -1;
	}

	if (extent_item->type == BTRFS_FILE_EXTENT_INLINE) {/* inline file */
		/* we fake a extent here, and PVT of inode will tell us */
		offset = path.offsets[0] + sizeof(struct btrfs_header)
			+ path.item.offset
			+ offsetof(struct btrfs_file_extent_item, disk_bytenr);
		inode->next_extent.len =
			(inode->size + sec_size - 1) >> sec_shift;
	} else {
		offset = extent_item->disk_bytenr + extent_item->offset;
		inode->next_extent.len =
			(extent_item->num_bytes + sec_size - 1) >> sec_shift;
	}
	inode->next_extent.pstart =
		logical_physical(offset) >> sec_shift;
	pvt = (struct btrfs_pvt_inode *)inode->pvt;
	pvt->offset = offset;
	return 0;
}

static uint32_t btrfs_getfssec(struct file *file, char *buf, int sectors,
					char *have_more)
{
	u32 ret;
	struct btrfs_pvt_inode *pvt =
			(struct btrfs_pvt_inode *)file->inode->pvt;
	u32 off = pvt->offset % BTRFS_SS;
	char handle_inline = 0;

	if (off && !file->offset) {/* inline file first read patch */
		debug("%s handle_inline off=%d file->offset=%lld, file->inode->size=%d\n", __func__, off, file->offset, file->inode->size);
		file->inode->size += off;
		handle_inline = 1;
		/* Read one extra sector when the inline file goes past the sector. */
		if (((file->inode->size % BTRFS_SS)+off) > BTRFS_SS)
			sectors++;
	}
	ret = generic_getfssec(file, buf, sectors, have_more);
	if (!ret)
		return ret;

	off = pvt->offset % BTRFS_SS;
	if (handle_inline) {/* inline file patch */
		debug("%s handle_inline off=%d\n", __func__, off);
		ret -= off;
		memcpy(buf, buf + off, ret);
	}

	return ret;
}

static void btrfs_get_fs_tree(struct btrfs_info *fs)
{
	struct btrfs_disk_key search_key;
	struct btrfs_path path;
	struct btrfs_root_item *tree;
	char subvol_ok = 0;

	/* check if subvol is filled by installer */
	if (*subvolname) {
		search_key.objectid = BTRFS_FS_TREE_OBJECTID;
		search_key.type = BTRFS_ROOT_REF_KEY;
		search_key.offset = 0;
		clear_path(&path);
		if (search_tree(fs, __le64_to_cpu(sb.root), &search_key, &path))
			next_slot(fs, &search_key, &path);
		do {
			do {
				struct btrfs_root_ref *ref;
				int pathlen;

				if (btrfs_comp_keys_type(&search_key,
							&path.item.key))
					break;
				ref = (struct btrfs_root_ref *)path.data;
				pathlen =
				path.item.size - sizeof(struct btrfs_root_ref);

				debug("sub_vol found %s\n", (char *)(ref+1));
				if ((!strncmp((char *)(ref + 1),
						subvolname, pathlen)) &&
						pathlen == strlen(subvolname)) {
					subvol_ok = 1;
					break;
				}
			} while (!next_slot(fs, &search_key, &path));
			if (subvol_ok)
				break;
			if (btrfs_comp_keys_type(&search_key, &path.item.key))
				break;
		} while (!next_leaf(fs, &search_key, &path));
		if (!subvol_ok)
			puts("no subvol found\n");
	}
	/* find fs_tree from tree_root */
	if (subvol_ok)
		search_key.objectid = path.item.key.offset;
	else /* "default" volume */
		search_key.objectid = BTRFS_FS_TREE_OBJECTID;
	search_key.type = BTRFS_ROOT_ITEM_KEY;
	search_key.offset = -1;
	clear_path(&path);
	search_tree(fs, (sb.root), &search_key, &path);
	tree = (struct btrfs_root_item *)path.data;
	fs_tree = tree->bytenr;
}

/* init. the fs meta data, return the block size shift bits. */
int btrfs_fs_init(struct btrfs_info *fs)
{
	if (!crc_table_built) { /*Build crc table once*/
		btrfs_init_crc32c();
		crc_table_built = 1;
	}

	btrfs_read_super_block(fs);
	if (strncmp((char *)(&sb.magic), BTRFS_MAGIC, sizeof(sb.magic)))
		return -1;
	tree_buf = malloc(max(sb.nodesize, sb.leafsize));
	if (!tree_buf)
		return -1;

	btrfs_read_sys_chunk_array();
	btrfs_read_chunk_tree(fs);
	btrfs_get_fs_tree(fs);
	fs->root = btrfs_iget_root(fs);
	parent_inode = *(fs->root);

	printf("BtrFS init: Max node or leaf size %d\n",
		max(sb.nodesize, sb.leafsize));
	return 1;
}
static inline uint16_t file_to_handle(struct file *file)
{
	return file ? (file - files) + 1 : 0;
}

static inline struct file *handle_to_file(uint16_t handle)
{
	return handle ? &files[handle - 1] : NULL;
}

/*
 * Free a refcounted inode
 */
void put_inode(struct inode *inode)
{
	while (inode && --inode->refcnt == 0) {
		struct inode *dead = inode;
		inode = inode->parent;
		if (dead->name)
			free((char *)dead->name);
		free(dead);
	}
}

/*
 * Get a new inode structure
 */
struct inode *alloc_inode(struct btrfs_info *fs, uint32_t ino, size_t data)
{
	struct inode *inode = malloc(sizeof(struct inode) + data);

	if (inode) {
		inode->fs = fs;
		inode->ino = ino;
		inode->refcnt = 1;
	}

	return inode;
}

/*
 * Get an empty file structure
 */
static struct file *alloc_file(void)
{
	int i;
	struct file *file = files;

	for (i = 0; i < BTRFS_MAX_OPEN; i++) {
		if (!file->fs)
			return file;

		file++;
	}

	return NULL;
}

/*
 * Close and free a file structure
 */
static inline void free_file(struct file *file)
{
	memset(file, 0, sizeof *file);
}

void close_file(struct file *file)
{
	if (file->inode) {
		file->offset = 0;
		put_inode(file->inode);
	}
}

void btrfs_close_file(struct file *file)
{
	if (file->fs)
		close_file(file);
	free_file(file);
}

void btrfs_mangle_name(char *dst, const char *src)
{
	char *p = dst, ch, len;
	int i = BTRFS_FILENAME_MAX-1;

	while ((src[0] == '/')&&(src[1] != '\0'))
		src++;

	len = strlen(src);
	ch = *src;
	while (!isspace(ch)) {
		if (*src == '/') {
			if (src[1] == '/') {
				src++;
				i--;
				continue;
			}
		}
		if (!len)
			break;
		i--;
		len--;
		*dst++ = *src++;
		ch = *src;
	}
	while (1) {
		if (dst == p)
			break;
		if (dst[-1] != '/')
			break;
		if ((dst[-1] == '/') && ((dst - 1) == p))
			break;

		dst--;
		i++;
	}

	i++;
	for (; i > 0; i--)
		*dst++ = '\0';

}

int searchdir(const char *name)
{
	struct inode *inode = NULL;
	struct inode *parent = &parent_inode;
	struct file *file;
	char *pathbuf = NULL;
	char *part, *p, echar;
	int symlink_count = BTRFS_MAX_SYMLINK_CNT;

	file = alloc_file();
	if (!(file))
		goto err_no_close;

	p = pathbuf = strdup(name);
	if (!pathbuf)
		goto err;

	do {
got_link:
		if (*p == '/') {
			put_inode(parent);
			parent =  &parent_inode;
		}

		do {
			inode = get_inode(parent);

			while (*p == '/')
				p++;

			if (!*p)
				break;

			part = p;
			while ((echar = *p) && echar != '/')
				p++;
			*p++ = '\0';
			if (part[0] == '.' && part[1] == '.' &&
						part[2] == '\0') {
				if (inode->parent) {
					put_inode(parent);
					parent = get_inode(inode->parent);
					put_inode(inode);
					inode = NULL;
					if (!echar) {
						/* Terminal double dots */
						inode = parent;
						parent = inode->parent ?
						get_inode(inode->parent) : NULL;
					}
				}
			} else if (part[0] != '.' || part[1] != '\0') {
				inode = btrfs_iget(part, parent);
				if (!inode)
					goto err;
				if (inode->mode == BTRFS_DT_LNK) {
					char *linkbuf, *q;
					int name_len = echar ? strlen(p) : 0;
					int total_len = inode->size +
							name_len + 2;
					int link_len;

					if (--symlink_count == 0 ||
					total_len > BTRFS_MAX_SYMLINK_BUF)
						goto err;

					linkbuf = malloc(total_len);
					if (!linkbuf)
						goto err;

					link_len =
						btrfs_readlink(inode, linkbuf);
					if (link_len <= 0) {
						free(linkbuf);
						goto err;
					}

					q = linkbuf + link_len;

					if (echar) {
						if (link_len > 0 &&
								q[-1] != '/')
							*q++ = '/';
						memcpy(q, p, name_len+1);
					} else {
						*q = '\0';
					}

					free(pathbuf);
					p = pathbuf = linkbuf;
					put_inode(inode);
					inode = NULL;
					goto got_link;
				}

				inode->name = (u8 *)strdup(part);

				inode->parent = parent;
				parent = NULL;

				if (!echar)
					break;

				if (inode->mode != BTRFS_DT_DIR)
					goto err;

				parent = inode;
				inode = NULL;
			}
		} while (echar);
	} while (0);

	free(pathbuf);
	pathbuf = NULL;
	put_inode(parent);
	parent = NULL;

	if (!inode)
		goto err;

	file->inode  = inode;
	file->offset = 0;

	return file_to_handle(file);

err:
	put_inode(inode);
	put_inode(parent);
	if (pathbuf != NULL)
		free(pathbuf);
	btrfs_close_file(file);
err_no_close:
	return -1;
}

int btrfs_open_file(const char *name, struct com32_filedata *filedata)
{
	int rv;
	struct file *file;
	char mangled_name[BTRFS_FILENAME_MAX];

	btrfs_mangle_name(mangled_name, name);
	rv = searchdir(mangled_name);
	if (rv < 0)
		return rv;

	file = handle_to_file(rv);
	filedata->size      = file->inode->size;
	filedata->handle    = rv;

	return rv;
}

static void get_next_extent(struct inode *inode)
{
	/* The logical start address that we care about... */
	uint32_t lstart = inode->this_extent.lstart + inode->this_extent.len;

	if (btrfs_next_extent(inode, lstart))
		inode->next_extent.len = 0; /* ERROR */
	inode->next_extent.lstart = lstart;
}

int getfssec(struct com32_filedata *filedata, char * buf)
{
	int sectors;
	char have_more;
	uint32_t bytes_read;
	struct file *file;
	if (filedata->size >= BTRFS_SS) {
		sectors = filedata->size/BTRFS_SS;
		sectors += (filedata->size%BTRFS_SS) ? 1 : 0;
	} else
		sectors = 2;

	file = handle_to_file(filedata->handle);

	bytes_read = btrfs_getfssec(file, buf, sectors, &have_more);

	return bytes_read;
}

uint32_t generic_getfssec(struct file *file, char *buf,
				int sectors, char *have_more)
{
	struct inode *inode = file->inode;
	uint32_t bytes_read = 0;
	uint32_t bytes_left = inode->size - file->offset;
	uint32_t sectors_left = (bytes_left + BTRFS_SS - 1) >> 9;
	uint32_t lsector;

	if (sectors > sectors_left)
		sectors = sectors_left;

	if (!sectors)
		return 0;

	lsector = file->offset >> 9;

	if (lsector < inode->this_extent.lstart ||
		lsector >= inode->this_extent.lstart + inode->this_extent.len) {
		/* inode->this_extent unusable, maybe next_extent is... */
		inode->this_extent = inode->next_extent;
	}

	if (lsector < inode->this_extent.lstart ||
	lsector >= inode->this_extent.lstart + inode->this_extent.len) {
		/* Still nothing useful... */
		inode->this_extent.lstart = lsector;
		inode->this_extent.len = 0;
	} else {
		/* We have some usable information */
		uint32_t delta = lsector - inode->this_extent.lstart;
		inode->this_extent.lstart = lsector;
		inode->this_extent.len -= delta;
		inode->this_extent.pstart
		    = next_psector(inode->this_extent.pstart, delta);
	}

	while (sectors) {
		uint32_t chunk;
		size_t len;

		while (sectors > inode->this_extent.len) {
			if (!inode->next_extent.len ||
				inode->next_extent.lstart !=
				inode->this_extent.lstart +
						inode->this_extent.len)
				get_next_extent(inode);
			if (!inode->this_extent.len) {
				/* Doesn't matter if it's contiguous... */
				inode->this_extent = inode->next_extent;
				if (!inode->next_extent.len) {
					sectors = 0; /* Failed to get anything*/
					break;
				}
			} else if (inode->next_extent.len &&
				inode->next_extent.pstart ==
					next_pstart(&inode->this_extent)) {
				/* Coalesce extents and loop */
				inode->this_extent.len +=
						inode->next_extent.len;
			} else {
				/* Discontiguous extents */
				break;
			}
		}

		chunk = min(sectors, (int)inode->this_extent.len);
		len = chunk << 9;

		if (inode->this_extent.pstart == BTRFS_EXTENT_ZERO) {
			memset(buf, 0, len);
		} else {
			btrfs_block_dev_desc->block_read(
				btrfs_block_dev_desc->dev, part_info->start +
				(inode->this_extent.pstart), chunk, buf);
			inode->this_extent.pstart += chunk;
		}

		 buf += len;
		sectors -= chunk;
		bytes_read += len;
		inode->this_extent.lstart += chunk;
		inode->this_extent.len -= chunk;
	}

	bytes_read = min(bytes_read, bytes_left);
	file->offset += bytes_read;

	if (have_more)
		*have_more = bytes_read < bytes_left;

	return bytes_read;
}

/*
 * Open a directory
 */
struct _DIR_ *opendir(const char *path)
{
	int rv;
	struct file *file;
	rv = searchdir(path);
	if (rv < 0)
		return NULL;

	file = handle_to_file(rv);

	if (file->inode->mode != BTRFS_DT_DIR) {
		btrfs_close_file(file);
		return NULL;
	}

	return (struct _DIR_ *)file;
}

/*
 * Read one directory entry at one time
 */
struct btrfs_dirent *readdir(struct _DIR_ *dir)
{
	static struct btrfs_dirent buf;
	struct file *dd_dir = (struct file *)dir;
	int rv = -1;

	if (dd_dir)
		rv = btrfs_readdir(dd_dir, &buf);

	return rv < 0 ? NULL : &buf;
}

/*
 *  Btrfs file-system Interface
 *
 */

struct btrfs_info fs;

/*
 *  mount btrfs file-system
 */
int btrfs_probe(block_dev_desc_t *rbdd, disk_partition_t *info)
{
	btrfs_block_dev_desc = rbdd;
	part_info = info;
	btr_part_offset = info->start;
	if (btrfs_fs_init(&fs) < 0) {
		puts("btrfs probe failed\n");
		return -1;
	}

	return 0;
}

/*
 *  Read file data
 */
int btrfs_read_file(const char *filename, void *buf, loff_t offset, loff_t len,
                  loff_t *actread)
{
	int file_len = 0;
	int len_read;
	struct com32_filedata filedata;
	int handle;
	if (offset != 0) {
		puts("** Cannot support non-zero offset **\n");
		return -1;
	}

	handle = btrfs_open_file(filename, &filedata);
	if (handle < 0) {
		debug("** File not found %s Invalid handle**\n", filename);
		return -1;
	}

	/*file handle is valid get the size of the file*/
	file_len = filedata.size;
	if (len == 0)
		len = file_len;

	len_read = getfssec(&filedata, (char *)buf);
	if (len_read != len) {
		debug("** Unable to read file %s **\n", filename);
		return -1;
	}

	*actread = len_read;
	return len_read;
}

/*
 * Show directory entries
 */
int btrfs_ls(const char *dirn)
{
	struct btrfs_dirent *de;
	char *dirname = (char *)dirn;
	struct _DIR_ *dir;

	if (*dirname == '/' && *(dirname+1) == 0)
		*dirname = '.';

	while ((dirname[0] == '/')&&(dirname[1] != '\0'))
		dirname++;

	dir = opendir(dirname);
	if (dir == NULL)
		return -1;

	/* readdir prints contents on media*/
	de = readdir(dir);
	while (de != NULL)
		de = readdir(dir);

	return 0;
}

/*
 *  umount btrfs file-system
 */
void btrfs_close(void)
{
}
