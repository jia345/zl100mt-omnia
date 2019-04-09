 
#ifndef IOT_CONFIG_H
#define IOT_CONFIG_H

#include <stdio.h>
#include "list.h"

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

#define iot_new0(type,n)	(type*)calloc(sizeof(type),n)

typedef struct _iot_cfg_item{
	T_IOT_LISTHEAD link;
	char *key;
	char *value;
	char *old_value;
	int  byuser;
} T_IOT_CFG_ITEM;

typedef struct _iot_cfg_section{
	T_IOT_LISTHEAD link;
	char *name;
	T_IOT_LISTHEAD items;
} T_IOT_CFG_SEC;

typedef struct _iot_config{
	char *filename;
	FILE *file;
	T_IOT_LISTHEAD sections;
	int modified;
} T_IOT_CFG;

T_IOT_CFG * iot_cfg_new(const char *filename);

const char *iot_cfg_get_str(T_IOT_CFG *p_cfg, const char *section, const char *key, const char *default_string);
int         iot_cfg_get_int(T_IOT_CFG *p_cfg, const char *section, const char *key, int default_value);
float       iot_cfg_get_flt(T_IOT_CFG *p_cfg, const char *section, const char *key, float default_value);

void iot_cfg_set_str(T_IOT_CFG *p_cfg, const char *section, const char *key, const char *value);
void iot_cfg_set_int(T_IOT_CFG *p_cfg, const char *section, const char *key, int value);

int iot_cfg_sync(T_IOT_CFG *p_cfg);
int iot_cfg_same_2(T_IOT_CFG *config1, T_IOT_CFG *config2);
void iot_cfg_set_filename(T_IOT_CFG *lpconfig, const char *filename);
const char* iot_cfg_get_filename(T_IOT_CFG *lpconfig);
int iot_cfg_has_sec(T_IOT_CFG *lpconfig, const char *section);
void iot_cfg_clean_sec(T_IOT_CFG *lpconfig, const char *section);
int iot_cfg_needs_commit(const T_IOT_CFG *lpconfig);
void iot_cfg_destroy(T_IOT_CFG *cfg);
	

#endif
