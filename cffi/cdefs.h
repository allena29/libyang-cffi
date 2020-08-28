/*
 * Copyright (c) 2018-2019 Robin Jarry
 * SPDX-License-Identifier: MIT
 */

struct ly_ctx;

#define LY_CTX_ALLIMPLEMENTED ...
#define LY_CTX_TRUSTED ...
#define LY_CTX_NOYANGLIBRARY ...
#define LY_CTX_DISABLE_SEARCHDIRS ...
#define LY_CTX_DISABLE_SEARCHDIR_CWD ...
#define LY_CTX_PREFER_SEARCHDIRS ...
#define LYD_OPT_CONFIG ...
#define LYD_OPT_TRUSTED ...
#define LYP_WITHSIBLINGS ...
#define LYD_PATH_OPT_UPDATE ...
#define LYD_OPT_EXPLICIT ...
#define LYD_OPT_DESTRUCT ...
#define LYD_OPT_STRICT ...

struct ly_ctx *ly_ctx_new(const char *, int);
int ly_ctx_set_searchdir(struct ly_ctx *, const char *);
void ly_ctx_destroy(struct ly_ctx *, void *);

typedef enum {
	LY_LLERR,
	LY_LLWRN,
	LY_LLVRB,
	LY_LLDBG,
	...
} LY_LOG_LEVEL;

struct ly_err_item {
	char *msg;
	char *path;
	char *apptag;
	struct ly_err_item *next;
	...;
};

#define LY_LOLOG ...
#define LY_LOSTORE ...
#define LY_LOSTORE_LAST ...
int ly_log_options(int);

LY_LOG_LEVEL ly_verb(LY_LOG_LEVEL);
extern "Python" void lypy_log_cb(LY_LOG_LEVEL, const char *, const char *);
void ly_set_log_clb(void (*)(LY_LOG_LEVEL, const char *, const char *), int);
struct ly_err_item *ly_err_first(const struct ly_ctx *);
void ly_err_clean(struct ly_ctx *, struct ly_err_item *);

struct lys_module {
	const char *name;
	const char *prefix;
	const char *dsc;
	const char *filepath;
	uint8_t rev_size;
	uint8_t features_size;
	struct lys_revision *rev;
	struct lys_feature *features;
	...;
};

#define LY_REV_SIZE 11
struct lys_revision {
	char date[LY_REV_SIZE];
	uint8_t ext_size;
	struct lys_ext_instance **ext;
	const char *dsc;
	const char *ref;
};

#define LYS_FENABLED ...
struct lys_feature {
	const char *name;
	const char *dsc;
	const char *ref;
	uint16_t flags;
	uint8_t iffeature_size;
	struct lys_iffeature *iffeature;
	struct lys_module *module;
	...;
};

#define LYS_IFF_NOT ...
#define LYS_IFF_AND ...
#define LYS_IFF_OR ...
#define LYS_IFF_F ...
struct lys_iffeature {
	uint8_t *expr;
	struct lys_feature **features;
	...;
};

int lys_features_enable(const struct lys_module *, const char *);
int lys_features_disable(const struct lys_module *, const char *);
int lys_features_state(const struct lys_module *, const char *);

struct lys_ext {
	const char *name;
	struct lys_module *module;
	...;
};

struct lys_ext_instance {
	struct lys_ext *def;
	const char *arg_value;
	...;
};

struct lys_restr {
	const char *expr;
	...;
};

typedef enum {
	LY_TYPE_DER,
	LY_TYPE_BINARY,
	LY_TYPE_BITS,
	LY_TYPE_BOOL,
	LY_TYPE_DEC64,
	LY_TYPE_EMPTY,
	LY_TYPE_ENUM,
	LY_TYPE_IDENT,
	LY_TYPE_INST,
	LY_TYPE_LEAFREF,
	LY_TYPE_STRING,
	LY_TYPE_UNION,
	LY_TYPE_INT8,
	LY_TYPE_UINT8,
	LY_TYPE_INT16,
	LY_TYPE_UINT16,
	LY_TYPE_INT32,
	LY_TYPE_UINT32,
	LY_TYPE_INT64,
	LY_TYPE_UINT64,
	LY_TYPE_UNKNOWN,
	...
} LY_DATA_TYPE;

struct lys_type_info_binary {
	struct lys_restr *length;
};

struct lys_type_bit {
	const char *name;
	const char *dsc;
	uint32_t pos;
	...;
};

struct lys_type_info_bits {
	struct lys_type_bit *bit;
	unsigned int count;
};

struct lys_type_info_dec64 {
	struct lys_restr *range;
	...;
};

struct lys_type_enum {
	const char *name;
	const char *dsc;
	...;
};

struct lys_type_info_enums {
	struct lys_type_enum *enm;
	unsigned int count;
};

struct lys_type_info_num {
	struct lys_restr *range;
};

struct lys_type_info_lref {
	const char *path;
	struct lys_node_leaf* target;
	int8_t req;
};

struct lys_type_info_str {
	struct lys_restr *length;
	struct lys_restr *patterns;
	unsigned int pat_count;
	...;
};

struct lys_type_info_union {
	struct lys_type *types;
	unsigned int count;
	int has_ptr_type;
};

union lys_type_info {
	struct lys_type_info_binary binary;
	struct lys_type_info_bits bits;
	struct lys_type_info_dec64 dec64;
	struct lys_type_info_enums enums;
	struct lys_type_info_num num;
	struct lys_type_info_lref lref;
	struct lys_type_info_str str;
	struct lys_type_info_union uni;
	...;
};

struct lys_type {
	LY_DATA_TYPE base;
	uint8_t value_flags;
	uint8_t ext_size;
	struct lys_ext_instance **ext;
	struct lys_tpdf *der;
	struct lys_tpdf *parent;
	union lys_type_info info;
	...;
};

struct lys_tpdf {
	const char *name;
	const char *dsc;
	uint8_t ext_size;
	struct lys_ext_instance **ext;
	const char *units;
	struct lys_type type;
	const char *dflt;
	...;
};

typedef enum lys_nodetype {
	LYS_UNKNOWN,
	LYS_CONTAINER,
	LYS_CHOICE,
	LYS_LEAF,
	LYS_LEAFLIST,
	LYS_LIST,
	LYS_ANYXML,
	LYS_CASE,
	LYS_NOTIF,
	LYS_RPC,
	LYS_INPUT,
	LYS_OUTPUT,
	LYS_GROUPING,
	LYS_USES,
	LYS_AUGMENT,
	LYS_ACTION,
	LYS_ANYDATA,
	LYS_EXT,
	...
} LYS_NODE;

#define LYS_CONFIG_W ...
#define LYS_CONFIG_R ...
#define LYS_CONFIG_SET ...
#define LYS_USERORDERED ...
#define LYS_MAND_TRUE ...
#define LYS_STATUS_DEPRC ...
#define LYS_STATUS_OBSLT ...

struct lys_node {
	const char *name;
	const char *dsc;
	uint16_t flags;
	uint8_t ext_size;
	uint8_t iffeature_size;
	struct lys_ext_instance **ext;
	struct lys_iffeature *iffeature;
	LYS_NODE nodetype;
	...;
};

struct lys_node_container {
	uint8_t must_size;
	struct lys_restr *must;
	const char *presence;
	...;
};

struct lys_node_leaf {
	uint8_t must_size;
	struct lys_restr *must;
	struct lys_type type;
	const char *units;
	const char *dflt;
	...;
};

struct lys_node_leaflist {
	uint8_t must_size;
	struct lys_restr *must;
	struct lys_type type;
	const char *units;
	uint32_t min;
	uint32_t max;
	uint8_t dflt_size;
	const char **dflt;
	...;
};

struct lys_node_list {
	uint8_t must_size;
	struct lys_restr *must;
	uint8_t keys_size;
	struct lys_node_leaf **keys;
	uint32_t min;
	uint32_t max;
	...;
};

union ly_set_set {
	struct lys_node **s;
	struct lyd_node **d;
	...;
};

struct ly_set {
	unsigned int size;
	unsigned int number;
	union ly_set_set set;
};

const struct lys_module *ly_ctx_load_module(struct ly_ctx *, const char *, const char *);
const struct lys_module *ly_ctx_get_module_iter(const struct ly_ctx *, uint32_t *);
const struct lys_module *ly_ctx_get_module(const struct ly_ctx *, const char *, const char *, int);
struct ly_set *ly_ctx_find_path(struct ly_ctx *, const char *);
void ly_set_free(struct ly_set *set);
const struct lys_node_list *lys_is_key(const struct lys_node_leaf *, uint8_t *);

#define LYS_GETNEXT_WITHCHOICE ...
#define LYS_GETNEXT_WITHCASE ...
#define LYS_GETNEXT_WITHGROUPING ...
#define LYS_GETNEXT_WITHINOUT ...
#define LYS_GETNEXT_WITHUSES ...
#define LYS_GETNEXT_INTOUSES ...
#define LYS_GETNEXT_INTONPCONT ...
#define LYS_GETNEXT_PARENTUSES ...
#define LYS_GETNEXT_NOSTATECHECK ...

const struct lys_node *lys_getnext(const struct lys_node *, const struct lys_node *, const struct lys_module *, int);
char *lys_data_path(const struct lys_node *);
char *lys_path(const struct lys_node *, int);
struct lys_module *lys_node_module(const struct lys_node *);
struct lys_module *lys_main_module(const struct lys_module *);
struct lys_node *lys_parent(const struct lys_node *);

typedef enum {
	LYS_OUT_UNKNOWN,
	LYS_OUT_YANG,
	LYS_OUT_YIN,
	LYS_OUT_TREE,
	LYS_OUT_INFO,
	LYS_OUT_JSON,
	...
} LYS_OUTFORMAT;

int lys_print_mem(char **, const struct lys_module *, LYS_OUTFORMAT, const char *, int, int);
int lys_print_fd(int, const struct lys_module *, LYS_OUTFORMAT, const char *, int, int);

/* from libc, needed to free allocated strings */
void free(void *);

/* data based things */
typedef enum {
	LYD_UNKNOWN,
	LYD_XML,
	LYD_JSON,
	LYD_LYB
} LYD_FORMAT;


typedef union lyd_value_u {
    const char *binary;          /**< base64 encoded, NULL terminated string */
    struct lys_type_bit **bit;   /**< bitmap of pointers to the schema definition of the bit value that are set,
                                      its size is always the number of defined bits in the schema */
    int8_t bln;                  /**< 0 as false, 1 as true */
    int64_t dec64;               /**< decimal64: value = dec64 / 10^fraction-digits  */
    struct lys_type_enum *enm;   /**< pointer to the schema definition of the enumeration value */
    struct lys_ident *ident;     /**< pointer to the schema definition of the identityref value */
    struct lyd_node *instance;   /**< pointer to the instance-identifier target, note that if the tree was modified,
                                      the target (address) can be invalid - the pointer is correctly checked and updated
                                      by lyd_validate() */
    int8_t int8;                 /**< 8-bit signed integer */
    int16_t int16;               /**< 16-bit signed integer */
    int32_t int32;               /**< 32-bit signed integer */
    int64_t int64;               /**< 64-bit signed integer */
    struct lyd_node *leafref;    /**< pointer to the referenced leaf/leaflist instance in data tree */
    const char *string;          /**< string */
    uint8_t uint8;               /**< 8-bit unsigned integer */
    uint16_t uint16;             /**< 16-bit signed integer */
    uint32_t uint32;             /**< 32-bit signed integer */
    uint64_t uint64;             /**< 64-bit signed integer */
    void *ptr;                   /**< arbitrary data stored using a type plugin */
} lyd_val;


struct lyd_attr {
  struct lyd_node *parent;
  struct lyd_attr *next;
  struct lys_ext_instance_complex *annotation;
  const char *name;
  const char *value_str;
  lyd_val value;
	...;
  //LY_DATA_TYPE _PACKED value_type;
  //uint8_t value_flags;
};


struct lyd_node {
    struct lys_node *schema;
    uint8_t validity;
    uint8_t dflt:1;
    uint8_t when_status:3;
    struct lyd_attr *attr;
    struct lyd_node *next;
    struct lyd_node *prev;
    struct lyd_node *parent;
	  uint32_t hash;
		struct hash_table *ht;
		struct lyd_node *child;

};

struct lyd_node_leaf_list {
    struct lys_node *schema;
    uint8_t validity;

    uint8_t dflt:1;
    uint8_t when_status:3;
		struct lyd_attr *attr;
    struct lyd_node *next;
    struct lyd_node *prev;
    struct lyd_node *parent;
    uint32_t hash;
		const char *value_str;
		lyd_val value;
		LY_DATA_TYPE value_type;
    uint8_t value_flags;
};

struct lyd_node *lyd_new_path(struct lyd_node*, const struct ly_ctx*, const char*, void*, int, int);
int lyd_print_file(FILE *f, const struct lyd_node *root, LYD_FORMAT format, int options);
int lyd_print_mem(char **, const struct lyd_node *root, LYD_FORMAT format, int options);
int lyd_merge(struct lyd_node*, const struct lyd_node*, int options);
struct ly_set *lyd_find_path(const struct lyd_node *ctx_node, const char *path);
struct lyd_node *lyd_parse_path(struct ly_ctx *ctx, const char *path, LYD_FORMAT format, int options);
struct lyd_node *lyd_parse_mem(struct ly_ctx *ctx, const char *data, LYD_FORMAT format, int options);
struct lyd_difflist *lyd_diff(struct lyd_node *first, struct lyd_node *second, int options);
char *lyd_path(const struct lyd_node *node);
void lyd_free(struct lyd_node *node);
void lyd_free_withsiblings(struct lyd_node *node);
void lyd_unlink(struct lyd_node *node);
/* extra functions */
const struct lys_ext_instance *lypy_find_ext(
const struct lys_ext_instance **, uint8_t,
const char *, const char *, const char *);
char *lypy_data_path_pattern(const struct lys_node *);
char *lypy_node_fullname(const struct lys_node *);
const struct lyd_node *lypy_get_root_node(const struct lyd_node *node);
int validate_data_tree(struct lyd_node *node, struct ly_ctx *ctx);
int lypy_get_netconf_annotated_nodes(struct lyd_node *node, struct ly_ctx *ctx);