#ifndef _BTRFS_H_
#define _BTRFS_H_

#include <asm/byteorder.h>
/* type that store on disk, but it is same as cpu type for i386 arch */

#define BTRFS_CURRENTDIR_MAX		15
#define BTRFS_MAX_OPEN			5
#define BTRFS_FILENAME_MAX		128
#define BTRFS_MAX_SYMLINK_CNT		20
#define BTRFS_MAX_SYMLINK_BUF		4096
#define BTRFS_SECTOR_SHIFT(fs)		((fs)->sector_shift)
#define BTRFS_IFTODT(mode)		(((mode) & 0170000) >> 12)
#define BTRFS_SECTOR_SIZE		0x200
#define BTRFS_SECTOR_BITS		9
#define BTRFS_EXTENT_ZERO		((uint32_t)-1) /* All-zero extent */
#define BTRFS_EXTENT_VOID		((uint32_t)-2) /* Invalid information */
#define BTRFS_DT_LNK			10
#define BTRFS_DT_REG			8
#define BTRFS_DT_DIR			4
#define EXTENT_SPECIAL(x)		((x) >= BTRFS_EXTENT_VOID)
#define BTRFS_MAX_SUBVOL_NAME		50

#define BTRFS_FILE			1
#define BTRFS_DIR			2
#define BTRFS_SYMLNK			7
#define BTRFS_SS			BTRFS_SECTOR_SIZE

extern char subvolname[BTRFS_MAX_SUBVOL_NAME];
struct _DIR_;

struct com32_filedata {
	size_t size;                /* File size */
	int blocklg2;               /* log2(block size) */
	uint16_t handle;            /* File handle */
};

struct btrfs_info {
	const struct fs_ops *fs_ops;
	struct device *fs_dev;
	void *btrfs_info;             /* The fs-specific information */
	int sector_shift, sector_size;
	int block_shift, block_size;
	struct inode *root, *cwd;           /* Root and current directories */
	char cwd_name[BTRFS_CURRENTDIR_MAX]; /* Current directory by name */
};
/*
 * Extent structure: contains the mapping of some chunk of a file
 * that is contiguous on disk.
 */
struct extent {
	uint64_t   pstart;
	uint32_t    lstart;         /* Logical start sector */
	uint32_t    len;            /* Number of contiguous sectors */
} __packed;


struct inode {
	struct btrfs_info *fs;  /* The filesystem inode is associated with */
	struct inode *parent;       /* Parent directory, if any */
	const u8 *name;           /* Name, valid for generic path search only */
	uint32_t          refcnt;
	uint32_t       mode;   /* FILE , DIR or SYMLINK */
	uint32_t     size;
	uint32_t     blocks; /* How many blocks the file take */
	uint32_t     ino;    /* Inode number */
	uint32_t     atime;  /* Access time */
	uint32_t     mtime;  /* Modify time */
	uint32_t     ctime;  /* Create time */
	uint32_t     dtime;  /* Delete time */
	uint32_t     flags;
	uint32_t     file_acl;
	struct extent this_extent, next_extent;
	u8         pvt[0]; /* Private filesystem data */
} __packed;
struct file {
	struct btrfs_info *fs;
	uint64_t offset;            /* for next read */
	struct inode *inode;        /* The file-specific information */
} __packed;

#define NAME_MAX 20
struct btrfs_dirent {
	uint32_t d_ino;
	uint32_t d_off;
	uint16_t d_reclen;
	uint16_t d_type;
	char d_name[NAME_MAX + 1];
};

#define btrfs_crc32c			crc32c_le

#define BTRFS_SUPER_INFO_OFFSET		(64 * 1024)
#define BTRFS_SUPER_INFO_SIZE		4096
#define BTRFS_MAX_LEAF_SIZE		16384
#define BTRFS_BLOCK_SHIFT		12

#define BTRFS_SUPER_MIRROR_MAX		3
#define BTRFS_SUPER_MIRROR_SHIFT	12
#define BTRFS_CSUM_SIZE			32
#define BTRFS_FSID_SIZE			16
#define BTRFS_LABEL_SIZE		256
#define BTRFS_SYSTEM_CHUNK_ARRAY_SIZE	2048
#define BTRFS_UUID_SIZE			16

#define BTRFS_MAGIC			"_BHRfS_M"

#define BTRFS_SUPER_FLAG_METADUMP	(1ULL << 33)

#define BTRFS_DEV_ITEM_KEY		216
#define BTRFS_CHUNK_ITEM_KEY		228
#define BTRFS_ROOT_REF_KEY		156
#define BTRFS_ROOT_ITEM_KEY		132
#define BTRFS_EXTENT_DATA_KEY		108
#define BTRFS_DIR_ITEM_KEY		84
#define BTRFS_INODE_ITEM_KEY		1

#define BTRFS_EXTENT_TREE_OBJECTID	2ULL
#define BTRFS_FS_TREE_OBJECTID		5ULL

#define BTRFS_FIRST_CHUNK_TREE_OBJECTID	256ULL

#define BTRFS_FILE_EXTENT_INLINE	0
#define BTRFS_FILE_EXTENT_REG		1
#define BTRFS_FILE_EXTENT_PREALLOC	2

#define BTRFS_MAX_LEVEL			8
#define BTRFS_MAX_CHUNK_ENTRIES		256

#define BTRFS_DEV_ITEMS_OBJECTID	1ULL

#define BTRFS_FT_REG_FILE		1
#define BTRFS_FT_DIR			2
#define BTRFS_FT_SYMLINK		7

#define ROOT_DIR_WORD			0x002f

struct btrfs_dev_item {
	uint64_t devid;
	uint64_t total_bytes;
	uint64_t bytes_used;
	uint32_t io_align;
	uint32_t io_width;
	uint32_t sector_size;
	uint64_t type;
	uint64_t generation;
	uint64_t start_offset;
	uint32_t dev_group;
	u8 seek_speed;
	u8 bandwidth;
	u8 uuid[BTRFS_UUID_SIZE];
	u8 fsid[BTRFS_UUID_SIZE];
} __packed;

struct btrfs_super_block {
	u8 csum[BTRFS_CSUM_SIZE];
	/* the first 4 fields must match struct btrfs_header */
	u8 fsid[BTRFS_FSID_SIZE];    /* FS specific uuid */
	uint64_t bytenr; /* this block number */
	uint64_t flags;

	/* allowed to be different from the btrfs_header from here own down */
	uint64_t magic;
	uint64_t generation;
	uint64_t root;
	uint64_t chunk_root;
	uint64_t log_root;

	/* this will help find the new super based on the log root */
	uint64_t log_root_transid;
	uint64_t total_bytes;
	uint64_t bytes_used;
	uint64_t root_dir_objectid;
	uint64_t num_devices;
	uint32_t sectorsize;
	uint32_t nodesize;
	uint32_t leafsize;
	uint32_t stripesize;
	uint32_t sys_chunk_array_size;
	uint64_t chunk_root_generation;
	uint64_t compat_flags;
	uint64_t compat_ro_flags;
	uint64_t incompat_flags;
	__le16 csum_type;
	u8 root_level;
	u8 chunk_root_level;
	u8 log_root_level;
	struct btrfs_dev_item dev_item;

	char label[BTRFS_LABEL_SIZE];

	uint64_t cache_generation;

	/* future expansion */
	uint64_t reserved[31];
	u8 sys_chunk_array[BTRFS_SYSTEM_CHUNK_ARRAY_SIZE];
} __packed;
struct btrfs_disk_key {
	uint64_t objectid;
	u8 type;
	uint64_t offset;
} __packed;

struct btrfs_stripe {
	uint64_t devid;
	uint64_t offset;
	u8 dev_uuid[BTRFS_UUID_SIZE];
} __packed;

struct btrfs_chunk {
	uint64_t length;
	uint64_t owner;
	uint64_t stripe_len;
	uint64_t type;
	uint32_t io_align;
	uint32_t io_width;
	uint32_t sector_size;
	__le16 num_stripes;
	__le16 sub_stripes;
	struct btrfs_stripe stripe;
} __packed __attribute__((__may_alias__));

struct btrfs_header {
	/* these first four must match the super block */
	u8 csum[BTRFS_CSUM_SIZE];
	u8 fsid[BTRFS_FSID_SIZE]; /* FS specific uuid */
	uint64_t bytenr; /* which block this node is supposed to live in */
	uint64_t flags;

	/* allowed to be different from the super from here on down */
	u8 chunk_tree_uuid[BTRFS_UUID_SIZE];
	uint64_t generation;
	uint64_t owner;
	uint32_t nritems;
	u8 level;
} __packed;

struct btrfs_item {
	struct btrfs_disk_key key;
	uint32_t offset;
	uint32_t size;
} __packed;

struct btrfs_leaf {
	struct btrfs_header header;
	struct btrfs_item items[];
} __packed;

struct btrfs_key_ptr {
	struct btrfs_disk_key key;
	uint64_t blockptr;
	uint64_t generation;
} __packed;

struct btrfs_node {
	struct btrfs_header header;
	struct btrfs_key_ptr ptrs[];
} __packed;

/* remember how we get to a node/leaf */
struct btrfs_path {
	uint64_t offsets[BTRFS_MAX_LEVEL];
	uint32_t itemsnr[BTRFS_MAX_LEVEL];
	uint32_t slots[BTRFS_MAX_LEVEL];
	/* remember last slot's item and data */
	struct btrfs_item item;
	u8 data[BTRFS_MAX_LEAF_SIZE];
} __packed;

/* store logical offset to physical offset mapping */
struct btrfs_chunk_map_item {
	uint64_t logical;
	uint64_t length;
	uint64_t devid;
	uint64_t physical;
} __packed;

struct btrfs_chunk_map {
	struct btrfs_chunk_map_item *map;
	uint32_t map_length;
	uint32_t cur_length;
} __packed;

struct btrfs_timespec {
	uint64_t sec;
	uint32_t nsec;
} __packed;

struct btrfs_inode_item {
	/* nfs style generation number */
	uint64_t generation;
	/* transid that last touched this inode */
	uint64_t transid;
	uint64_t size;
	uint64_t nbytes;
	uint64_t block_group;
	uint32_t nlink;
	uint32_t uid;
	uint32_t gid;
	uint32_t mode;
	uint64_t rdev;
	uint64_t flags;

	/* modification sequence number for NFS */
	uint64_t sequence;

	/*
	 * a little future expansion, for more than this we can
	 * just grow the inode item and version it
	 */
	uint64_t reserved[4];
	struct btrfs_timespec atime;
	struct btrfs_timespec ctime;
	struct btrfs_timespec mtime;
	struct btrfs_timespec otime;
} __packed __attribute__((__may_alias__));

struct btrfs_root_item {
	struct btrfs_inode_item inode;
	uint64_t generation;
	uint64_t root_dirid;
	uint64_t bytenr;
	uint64_t byte_limit;
	uint64_t bytes_used;
	uint64_t last_snapshot;
	uint64_t flags;
	uint32_t refs;
	struct btrfs_disk_key drop_progress;
	u8 drop_level;
	u8 level;
} __packed __attribute__((__may_alias__));

struct btrfs_dir_item {
	struct btrfs_disk_key location;
	uint64_t transid;
	__le16 data_len;
	__le16 name_len;
	u8 type;
} __packed __attribute__((__may_alias__));

struct btrfs_file_extent_item {
	uint64_t generation;
	uint64_t ram_bytes;
	u8 compression;
	u8 encryption;
	__le16 other_encoding; /* spare for later use */
	u8 type;
	uint64_t disk_bytenr;
	uint64_t disk_num_bytes;
	uint64_t offset;
	uint64_t num_bytes;
} __packed __attribute__((__may_alias__));

struct btrfs_root_ref {
	uint64_t dirid;
	uint64_t sequence;
	__le16 name_len;
} __packed;

/*
 * btrfs private inode information
 */
struct btrfs_pvt_inode {
	uint64_t offset;
} __packed;


int btrfs_probe(block_dev_desc_t *rbdd , disk_partition_t *info);

/*
 *search through disk and mount file-system
 */
int btrfs_fs_init(struct btrfs_info *fs);

/*
 *save inode in list
 */
void put_inode(struct inode *inode);

/*
 *memory allocation for new inode
 */
struct inode *alloc_inode(struct btrfs_info *fs, uint32_t ino, size_t data);

/*
 * open btrfs file
 */
int btrfs_open_file(const char *name, struct com32_filedata *filedata);
/*
 * reading data from file
 */
int getfssec(struct com32_filedata *filedata, char *buf);
uint32_t generic_getfssec(struct file *file, char *buf,
				int sectors, char *have_more);

/*
 * mount btrfs file-system
 */
int btrfs_probe(block_dev_desc_t *rbdd , disk_partition_t *info);

/*
 * listing file/directory on btrfs partition/disk
 */
int btrfs_ls(const char *);

/*
 * read file data
 */
int btrfs_read_file(const char *filename, void *buf, loff_t offset, loff_t len,
                  loff_t *actread);

/*
 * umount btrfs file-system
 */
void btrfs_close(void);

#define PVT(i) ((struct btrfs_pvt_inode *)((i)->pvt))

#endif
