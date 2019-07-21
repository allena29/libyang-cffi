/*
 * Copyright (c) 2018 Robin Jarry
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

struct ly_ctx;
#define LY_CTX_ALLIMPLEMENTED ...
#define LY_CTX_TRUSTED ...
#define LY_CTX_NOYANGLIBRARY ...
#define LY_CTX_DISABLE_SEARCHDIRS ...
#define LY_CTX_DISABLE_SEARCHDIR_CWD ...
#define LY_CTX_PREFER_SEARCHDIRS ...

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

struct lys_type_enum {
	const char *name;
	const char *dsc;
	...;
};

struct lys_type_info_enums {
	struct lys_type_enum *enm;
	unsigned int count;
};

struct lys_type_info_lref {
	const char *path;
	struct lys_node_leaf* target;
	int8_t req;
};

struct lys_type_info_union {
	struct lys_type *types;
	unsigned int count;
	int has_ptr_type;
};

struct lys_restr {
	const char* expr;
	const char* dsc;
	const char* ref;
	const char* eapptag;
	const char* emsg;
	...;
};

struct lys_type_info_str {
	struct lys_restr* length;
	struct lys_restr* patterns;
	int pat_count;
	...;
};

union lys_type_info {
	struct lys_type_info_bits bits;
	struct lys_type_info_enums enums;
	struct lys_type_info_lref lref;
	struct lys_type_info_union uni;
	struct lys_type_info_str str;
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

struct lys_node {
	const char *name;
	const char *dsc;
	uint16_t flags;
	uint8_t ext_size;
	struct lys_ext_instance **ext;
	LYS_NODE nodetype;
	...;
};

struct lys_node_container {
	const char *presence;
	...;
};

struct lys_node_leaf {
	struct lys_type type;
	const char *units;
	const char *dflt;
	...;
};

struct lys_node_leaflist {
	struct lys_type type;
	const char *units;
	uint32_t min;
	uint32_t max;
	uint8_t dflt_size;
	const char **dflt;
	...;
};

struct lys_node_list {
	uint8_t keys_size;
	struct lys_node_leaf **keys;
	uint32_t min;
	uint32_t max;
	...;
};

union ly_set_set {
	struct lys_node **s;
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

/* extra functions */
const struct lys_ext_instance *lypy_find_ext(
	const struct lys_ext_instance **, uint8_t,
	const char *, const char *, const char *);
char *lypy_data_path_pattern(const struct lys_node *);
char *lypy_node_fullname(const struct lys_node *);
// 
// union lyd_value_u {
//   	const char *binary;          /**< base64 encoded, NULL terminated string */
//  		struct lys_type_bit **bit;   /**< bitmap of pointers to the schema definition of the bit value that are set,
//                                   	its size is always the number of defined bits in the schema */
//     int8_t bln;                  /**< 0 as false, 1 as true */
//     int64_t dec64;               /**< decimal64: value = dec64 / 10^fraction-digits  */
//     struct lys_type_enum *enm;   /**< pointer to the schema definition of the enumeration value */
//     struct lys_ident *ident;     /**< pointer to the schema definition of the identityref value */
//     struct lyd_node *instance;   /**< pointer to the instance-identifier target, note that if the tree was modified,
//                                        the target (address) can be invalid - the pointer is correctly checked and updated
//                                       by lyd_validate() */
//     int8_t int8;                 /**< 8-bit signed integer */
// 		int16_t int16;               /**< 16-bit signed integer */
// 		int32_t int32;               /**< 32-bit signed integer */
// 		int64_t int64;               /**< 64-bit signed integer */
// 		struct lyd_node *leafref;    /**< pointer to the referenced leaf/leaflist instance in data tree */
// 		const char *string;          /**< string */
// 		uint8_t uint8;               /**< 8-bit unsigned integer */
// 		uint16_t uint16;             /**< 16-bit signed integer */
// 		uint32_t uint32;             /**< 32-bit signed integer */
// 		uint64_t uint64;             /**< 64-bit signed integer */
// 		void *ptr;                   /**< arbitrary data stored using a type plugin */
// } lyd_val;
//
// struct lys_ext_instance_complex {
//     struct lys_ext *def;             /**< definition of the instantiated extension, the plugin's type is #LYEXT_COMPLEX */
//     void *parent;                    /**< pointer to the parent element holding the extension instance(s), use
//                                           ::lys_ext_instance#parent_type to access the schema element */
//     const char *arg_value;           /**< value of the instance's argument, if defined */
//     uint16_t flags;                  /**< [extension flags](@ref extflags) */
//     uint8_t ext_size;                /**< number of elements in #ext array */
//     uint8_t insubstmt_index;         /**< since some of the statements can appear multiple times, it is needed to
//                                           keep the position of the specific statement instance which contains
//                                           this extension instance. Order of both, the extension and the statement,
//                                           instances is the same. The index is filled only for LYEXT_SUBSTMT_BASE,
//                                           LYEXT_SUBSTMT_DEFAULT and LYEXT_SUBSTMT_UNIQUE values of the
//                                           ::lys_ext_instance#insubstmt member. To get the correct pointer to the
//                                           data connected with the index, use lys_ext_instance_substmt() */
//     uint8_t insubstmt;               /**< #LYEXT_SUBSTMT - id for the case the extension instance is actually inside
//                                           some of the node's members (substatements). libyang does not store extension
//                                           instances for all possible statements to save some, commonly unused, space. */
//     uint8_t parent_type;             /**< #LYEXT_PAR - type of the parent structure */
//     uint8_t ext_type;                /**< extension type (#LYEXT_TYPE) */
//     uint8_t padding;                 /**< 32b padding */
//     struct lys_ext_instance **ext;   /**< array of pointers to the extension instances */
//     void *priv;                      /**< private caller's data, not used by libyang */
//     struct lys_module *module;       /**< pointer to the extension instance's module (mandatory) */
//     LYS_NODE nodetype;               /**< LYS_EXT */
//
//     /* to this point the structure is compatible with the generic ::lys_ext_instance structure */
//     struct lyext_substmt *substmt;   /**< pointer to the plugin's list of substatements' information */
//     char content[1];                 /**< content of the extension instance */
// };
//
//
//
// struct lyd_attr {
// 	struct lyd_node parent;
// 	struct lyd_attr next;
// 	struct lys_ext_instance_complex annotation;
// 	const char name;
// 	const char value_str;
//
// 	...;   /** couldn't work out how to specify  - but we don't have to with ...
// 					   (of course it might be needed later on)
// 						LY_DATA_TYPE _PACKED	value_type
// 						type of the value in the node, mainly for union to avoid repeating of type detection
//
// 							uint8_t	value_flags
// 							value type flags **/
// } LYD_ATTR;
//
// struct lyd_node {
// 	struct lys_node schema;
// 	uint8_t validity;
// 	uint8_t dflt;
// 	uint8_t when_status;
// 	struct lyd_attr attr;
// 	struct lyd_node next;
// 	struct lyd_node prev;
// 	struct lyd_node parent;
// 	struct lyd_node child;
// } LYD_NODE;
