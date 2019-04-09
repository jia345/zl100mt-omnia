
#define MAX_LEN 1024


#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include "list.h"
#include "config.h"

extern int iot_err(const char *format, ...);
static int st_cfg_log(const char *format, ...)
{
	va_list ap;
	int len;
	char buf1[200];

	va_start(ap, format);
	len = vsnprintf(buf1, sizeof(buf1), format, ap);
	va_end(ap);

	iot_err("%s", buf1);
	
	return len;
}

/*
 * [reviewed]
 *
 * alloc mem for new item, init fields with parameters.
 * Parameter
 *     changed, this specifies whether this item is created by user-operation.
 *              It's should be set as true if it is created later by user. It's
 *              should be set as false if this func is called during parsing
 *              config file.
 *
 * Return
 *     pointer to newly allocated item.
 */
static T_IOT_CFG_ITEM * st_item_new(const char *key, const char *value, char byuser)
{
	T_IOT_CFG_ITEM *p_item = iot_new0(T_IOT_CFG_ITEM, 1);

	IOT_INIT_LIST_HEAD(&(p_item->link));
	p_item->key = strdup(key);
	p_item->value = strdup(value);
	p_item->old_value = strdup(value);
	p_item->byuser = byuser;
	
	return p_item;
}

/*
 * [reviewed]
 *
 * alloc mem for new section, init fields with parameters.
 *
 * Return
 *     pointer to newly allocated section.
 */
static T_IOT_CFG_SEC *st_sec_new(const char *name)
{
	T_IOT_CFG_SEC *p_sec = iot_new0(T_IOT_CFG_SEC, 1);

	IOT_INIT_LIST_HEAD(&(p_sec->link));
	IOT_INIT_LIST_HEAD(&(p_sec->items));
	p_sec->name = strdup(name);

	return p_sec;
}

/*
 * if value != old_value, it's modified.
 * Or if this is created later by user operation, it's also modified
 */
#if 0
static char st_item_modified(T_IOT_CFG_ITEM * item)
{
	if (strcmp(item->value, item->old_value) || item->byuser)
		return TRUE;
	else
		return FALSE;
}
#endif

static void st_item_destroy(T_IOT_CFG_ITEM *p_item)
{
	free(p_item->key);
	free(p_item->value);
	free(p_item->old_value);
	free(p_item);
}

static void st_sec_destroy(T_IOT_CFG_SEC *p_sec)
{
	T_IOT_CFG_ITEM *p_item;
	T_IOT_LISTHEAD *pos;
	T_IOT_LISTHEAD *n;

	free(p_sec->name);
	if (!iot_list_empty(&(p_sec->items))) {
		iot_list_for_each_safe(pos,n,&(p_sec->items)) {
			p_item = iot_list_entry(pos, T_IOT_CFG_ITEM, link);
			st_item_destroy(p_item);
		}
	}
	free(p_sec);
}

static void st_sec_add_item(T_IOT_CFG_SEC *p_sec, T_IOT_CFG_ITEM *p_item)
{
	iot_list_add_tail(&(p_item->link), &(p_sec->items));
}

static void st_cfg_add_sec(T_IOT_CFG *p_cfg, T_IOT_CFG_SEC *p_sec)
{
	iot_list_add_tail(&(p_sec->link), &(p_cfg->sections));
}

/*
 * If no valid char exists between [start,pos)? Including 'start', excluding 'pos'
 *
 * Return
 *     true:  if all chars are space or tab
 *     false: if not all chars are space
 */
static char st_is_1st_ch(const char *start, const char *pos)
{
	const char *p;

	for (p = start; p < pos; p++){
		if ((*p != ' ') && (*p != '\t')) {
			return FALSE;
		}
	}
	return TRUE;
}

/*
 * [Reviewed]
 *
 * Modify on original 'str', ensuring new str has no heading space and tab,
 * has no tailing space, tab, new-line and carriage.
 *
 * Modify on original buf.
 *
 * Precondition
 *     'str' must be terminated by '\0'
 *
 * Return
 *     NULL: If no valid chars after modification
 *     else: Pointer to new str after modification
 */
static char *st_pure_specifier(char *str)
{
	char *start = str;
	char *end;
	int len;

	if (start) {
		/* skip heading space, tab */
		while ((*start == ' ') || (*start == '\t'))
			start++;

		len = strlen(start);
		if (len) {
			/* rm tailing new-line, carriage, space, tab */
			for (end = &(start[len - 1]); end >= start; end--) {
				if (    ('\r' == *end)
				     || ('\n' == *end)
				     || ('\t' == *end)
				     || (' '  == *end)
				   )
				{
					*end = '\0';
				} else {
				   break;
				}
			}
		}

		if (!strlen(start))
			start = NULL;
	}

	return start;
}

/*
 * [reviewed]
 * parse a config file, add secs and keys
 */
static void st_cfg_parse(T_IOT_CFG *p_cfg)
{
	char buf[MAX_LEN];
	T_IOT_CFG_SEC *cur = NULL;
	
	if (NULL == p_cfg->file)
		return;

	while (fgets(buf, MAX_LEN, p_cfg->file) != NULL) { /* loop for each line */
		char *pos1;
		char *pos2;

		if ((pos1 = strchr(buf, '#'))) {               /* ignore lines start with '#' */
			if (st_is_1st_ch(buf, pos1)) {
				continue;
			}
		}

		if ((pos1 = strchr(buf, '['))) {               /* looks like a sec */
			if (st_is_1st_ch(buf, pos1)) {
				pos1++;
				if ((pos2 = strchr(pos1,']'))) {
					*pos2 = '\0';
					if ((pos1 = st_pure_specifier(pos1))) {
						cur = st_sec_new(pos1);
						st_cfg_add_sec(p_cfg, cur);
					} /* else: no valid char */
				} /* else: no ']', ignore the line */
			}
		} else if (cur && (pos2 = strchr(buf, '='))) { /* looks like a key, and we have a sec */
			*pos2 = '\0';
			pos2++;
			
			if (    (pos2 = st_pure_specifier(pos2))    /* pure value */
			     && (pos1 = st_pure_specifier(buf ))    /* pure key */
			   )
			{
				st_sec_add_item(cur, st_item_new(pos1, pos2, FALSE));
			} /* else: invalid key or value, ignore */
		} /* else: neither looks like sec nor key, ignore */
	} /* end of loop for each line */
}


static void st_item_set_val(T_IOT_CFG_ITEM *item, const char *value)
{
	if (strcmp(value, item->value)) {
		free(item->value);
		item->value = strdup(value);
	}
}

/*
 * [reviewed]
 * find sec by name
 */
static T_IOT_CFG_SEC *st_cfg_find_sec(T_IOT_CFG *p_cfg, const char *secname){
	T_IOT_CFG_SEC *p_sec;
	int found = 0;

	if (!iot_list_empty(&(p_cfg->sections))) {
		iot_list_for_each_entry(p_sec, &(p_cfg->sections), link, T_IOT_CFG_SEC) {
			if (!(strcmp(p_sec->name, secname))) {
				found = 1;
				break;
			}
		}
	}

	return (found ? p_sec : NULL);
}

static T_IOT_CFG_ITEM *st_sec_find_item(T_IOT_CFG_SEC *p_sec, const char *key)
{
	T_IOT_CFG_ITEM *p_item;
	int found = 0;

	if (!iot_list_empty(&(p_sec->items))) {
		iot_list_for_each_entry(p_item, &(p_sec->items), link, T_IOT_CFG_ITEM) {
			if (!strcmp(p_item->key, key)) {
				found = 1;
				break;
			}
		}
	}

	return (found ? p_item : NULL);
}

static void st_item_wr(T_IOT_CFG_ITEM *item, FILE *file)
{
	fprintf(file,"%s=%s\r\n",item->key,item->value);
}

static void st_sec_wr(T_IOT_CFG_SEC *sec, FILE *file)
{
	T_IOT_CFG_ITEM *p_item;
	
	fprintf(file,"[%s]\r\n",sec->name);
	if (!iot_list_empty(&(sec->items))) {
		iot_list_for_each_entry(p_item, &(sec->items), link, T_IOT_CFG_ITEM) {
			st_item_wr(p_item, file);
		}
	}
	fprintf(file,"\r\n");
}

/*
 * [reviewed]
 */
static int st_item_same_2(T_IOT_CFG_ITEM *item1, T_IOT_CFG_ITEM *item2)
{
	return (    (0 == strcmp(item1->key,   item2->key  ))
	         && (0 == strcmp(item1->value, item2->value))
	       );
}

/*
 * [reviewed]
 */
static int st_sec_same_2(T_IOT_CFG_SEC *p_sec1, T_IOT_CFG_SEC *p_sec2)
{
	T_IOT_CFG_ITEM *p_item1;
	T_IOT_CFG_ITEM *p_item2;
	T_IOT_LISTHEAD *p_head1 = &(p_sec1->items);
	T_IOT_LISTHEAD *p_head2 = &(p_sec2->items);
	T_IOT_LISTHEAD *p_link1 = iot_list_1st_link_or_null(p_head1);
	T_IOT_LISTHEAD *p_link2 = iot_list_1st_link_or_null(p_head2);
	int same;

	if (0 != strcmp(p_sec1->name, p_sec2->name)) { /* different name, different */
		same = 0;
	} else {
		while (p_link1 && p_link2) {
			p_item1 = iot_list_entry(p_link1, T_IOT_CFG_ITEM, link);
			p_item2 = iot_list_entry(p_link2, T_IOT_CFG_ITEM, link);

			if (!st_item_same_2(p_item1, p_item2))
				break;

			p_link1 = iot_list_is_last(p_link1, p_head1) ? NULL : p_link1->next;
			p_link2 = iot_list_is_last(p_link2, p_head2) ? NULL : p_link2->next;
		}

		/* if items on 2 lists are the same, p_lin1/2 should be both NULL now */
		same = (p_link1 == p_link2) ? 1 : 0;
	}

    return same;
}

/*
 * [reviewed]
 * load config file
 */
T_IOT_CFG * iot_cfg_new(const char *filename){
	T_IOT_CFG *p_cfg = NULL;
	FILE *p_file;

	if (filename != NULL){
		if ((p_file = fopen(filename, "rb")) != NULL) {
			p_cfg = iot_new0(T_IOT_CFG, 1);
			IOT_INIT_LIST_HEAD(&(p_cfg->sections));
			p_cfg->filename = strdup(filename);
			p_cfg->file = p_file;
			st_cfg_parse(p_cfg);
			fclose(p_cfg->file);
			p_cfg->file = NULL;
			p_cfg->modified = 0;
			/*iot_list_for_each_entry(p_sec, &(p_cfg->sections), link, T_IOT_CFG_SEC) {
				st_sec_wr(p_sec, stderr);
			}*/
		} /* else: open file failed, do nothing */
	} /* else: no file name provided, do nothing */
	return p_cfg;
}

void iot_cfg_set_filename(T_IOT_CFG *p_cfg, const char *filename)
{
    if (filename)
    	p_cfg->filename = strdup(filename);
}

const char* iot_cfg_get_filename(T_IOT_CFG *p_cfg)
{
    return p_cfg->filename;
}

/*
 * [reviewed]
 */
void iot_cfg_destroy(T_IOT_CFG *p_cfg)
{
	T_IOT_CFG_SEC *p_sec;
	T_IOT_LISTHEAD *pos, *n;

	if (p_cfg->filename != NULL)
		free(p_cfg->filename);

	if (!iot_list_empty(&(p_cfg->sections))) {
		iot_list_for_each_safe(pos, n, &(p_cfg->sections)) {
			p_sec = iot_list_entry(pos, T_IOT_CFG_SEC, link);
			st_sec_destroy(p_sec);
		}
	}

	free(p_cfg);
}

/*
 * [reviewed]
 */
const char *iot_cfg_get_str(T_IOT_CFG *p_cfg, const char *secname, const char *key, const char *defstr)
{
	T_IOT_CFG_SEC *p_sec;
	T_IOT_CFG_ITEM *p_item;
	
	if ((p_sec = st_cfg_find_sec(p_cfg, secname))) {
		if ((p_item = st_sec_find_item(p_sec, key)))
			return p_item->value;
	}
	
	return defstr;
}

/*
 * [reviewed]
 */
int iot_cfg_get_int(T_IOT_CFG *p_cfg,const char *secname, const char *key, int defval)
{
	const char *str;

	if ((str = iot_cfg_get_str(p_cfg, secname, key, NULL)))
		return atoi(str);
	else
		return defval;
}

/*
 * [reviewed]
 */
float iot_cfg_get_flt(T_IOT_CFG *p_cfg,const char *secname, const char *key, float defval){
	const char *str;
	float ret = defval;

	if ((str = iot_cfg_get_str(p_cfg, secname, key, NULL)))
		sscanf(str, "%f", &ret);

	return ret;
}

/*
 * [reviewed]
 *
 * If 'value' is NULL, means to rm the key, otherwise to set value or create a new one.
 * If sec not found, create a new sec. If key not found, create a new key.
 */
void iot_cfg_set_str(T_IOT_CFG *p_cfg,const char *secname, const char *key, const char *value)
{
	T_IOT_CFG_ITEM *item;
	T_IOT_CFG_SEC *p_sec;
	
	if ((p_sec = st_cfg_find_sec(p_cfg, secname))) { /* found sec */
		if ((item = st_sec_find_item(p_sec, key))){  /* found item */
			if (value)
				st_item_set_val(item, value);
			else
				iot_list_del(&(item->link));
		} else if (value) {                          /* item not found, create a new item */
				st_sec_add_item(p_sec, st_item_new(key, value, TRUE));
		}
	} else if (value) {                              /* sec not found, create a new sec */
		p_sec = st_sec_new(secname);
		st_cfg_add_sec(p_cfg, p_sec);
		st_sec_add_item(p_sec, st_item_new(key, value, TRUE));
	}
	p_cfg->modified++;
}

/*
 * [reviewed]
 */
void iot_cfg_set_int(T_IOT_CFG *p_cfg,const char *secname, const char *key, int value)
{
	char tmp[30];

	snprintf(tmp, 30, "%i", value);
	iot_cfg_set_str(p_cfg, secname, key, tmp);
	p_cfg->modified++;
}

/*
 * [reviewed]
 */
int iot_cfg_same_2(T_IOT_CFG *p_cfg1, T_IOT_CFG *p_cfg2)
{
	T_IOT_CFG_SEC *p_sec1;
	T_IOT_CFG_SEC *p_sec2;
	T_IOT_LISTHEAD *p_head1 = &(p_cfg1->sections);
	T_IOT_LISTHEAD *p_head2 = &(p_cfg2->sections);
	T_IOT_LISTHEAD *p_link1 = iot_list_1st_link_or_null(p_head1);
	T_IOT_LISTHEAD *p_link2 = iot_list_1st_link_or_null(p_head2);
	int same;

	while (p_link1 && p_link2) {
		p_sec1 = iot_list_entry(p_link1, T_IOT_CFG_SEC, link);
		p_sec2 = iot_list_entry(p_link2, T_IOT_CFG_SEC, link);

		if (!st_sec_same_2(p_sec1, p_sec2))
			break;

		p_link1 = iot_list_is_last(p_link1, p_head1) ? NULL : p_link1->next;
		p_link2 = iot_list_is_last(p_link2, p_head2) ? NULL : p_link2->next;
	}

	/* if items on 2 lists are the same, p_lin1/2 should be both NULL now */
	same = (p_link1 == p_link2) ? 1 : 0;

    return same;
}

/*
 * [reviewed]
 *
 * write whole cfg back to file specified by 'p_cfg->filename'
 *
 */
int iot_cfg_sync(T_IOT_CFG *p_cfg)
{
	FILE *file;
	T_IOT_CFG_SEC *p_sec;

	if (!(p_cfg->filename))
		return -1;

	if (!(file = fopen(p_cfg->filename, "w+b"))) {
		st_cfg_log("Could not write %s !",p_cfg->filename);
		return -1;
	}

	iot_list_for_each_entry(p_sec, &(p_cfg->sections), link, T_IOT_CFG_SEC) {
		st_sec_wr(p_sec, file);
	}

	fclose(file);
	p_cfg->modified = 0;

	return 0;
}

int iot_cfg_has_sec(T_IOT_CFG *p_cfg, const char *secname)
{
	return st_cfg_find_sec(p_cfg, secname) ? 1 : 0;
}

void iot_cfg_clean_sec(T_IOT_CFG *p_cfg, const char *secname)
{
	T_IOT_CFG_SEC *p_sec;

	if ((p_sec = st_cfg_find_sec(p_cfg, secname))) {
		iot_list_del(&(p_sec->link));
		st_sec_destroy(p_sec);
	}
	p_cfg->modified++;
}

int iot_cfg_needs_commit(const T_IOT_CFG *p_cfg)
{
	return p_cfg->modified > 0;
}
