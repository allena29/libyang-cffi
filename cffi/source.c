/*
 * Copyright (c) 2018-2019 Robin Jarry
 * SPDX-License-Identifier: MIT
 */

#include <libyang/libyang.h>

static const struct lys_ext_instance *
lypy_find_ext(const struct lys_ext_instance **ext, uint8_t ext_size,
	const char *name, const char *prefix, const char *arg_value)
{
	const struct lys_ext_instance *inst;
	const struct lys_module *module;
	const struct lys_ext *def;
	uint8_t i;

	if (!ext)
		goto notfound;

	for (i = 0; i < ext_size; i++) {
		inst = ext[i];
		def = inst->def;
		if (name && strcmp(def->name, name) != 0)
			continue;
		if (prefix) {
			module = lys_main_module(def->module);
			if (!module)
				goto notfound;
			if (strcmp(module->name, prefix) != 0)
				continue;
		}
		if (arg_value && inst->arg_value) {
			if (strcmp(arg_value, inst->arg_value) != 0)
				continue;
		}
		return inst;
	}

notfound:
	return NULL;
}

static char *lypy_data_path_pattern(const struct lys_node *node)
{
	const struct lys_module *prev_mod, *mod;
	char *xpath = NULL, *keys = NULL;
	struct ly_set *set = NULL;;
	size_t x;

	if (!node)
		goto cleanup;

	set = ly_set_new();
	if (!set)
		goto cleanup;

	while (node) {
		ly_set_add(set, (void *)node, 0);
		do {
			node = lys_parent(node);
		} while (node && !(node->nodetype & (
			LYS_CONTAINER | LYS_LIST | LYS_RPC)));
	}

	xpath = malloc(2048);
	if (!xpath)
		goto cleanup;
	keys = malloc(512);
	if (!keys)
		goto cleanup;

	x = 0;
	xpath[0] = '\0';

	prev_mod = NULL;
	for (int i = set->number - 1; i > -1; --i) {
		size_t k = 0;
		keys[0] = '\0';
		node = set->set.s[i];
		if (node->nodetype == LYS_LIST) {
			const struct lys_node_list *list;
			list = (const struct lys_node_list *)node;
			for (uint8_t j = 0; j < list->keys_size; j++) {
				k += sprintf(keys + k, "[%s='%%s']",
					list->keys[j]->name);
			}
		}

		mod = lys_node_module(node);
		if (mod && mod != prev_mod) {
			prev_mod = mod;
			x += sprintf(xpath + x, "/%s:%s%s",
				mod->name, node->name, keys);
		} else {
			x += sprintf(xpath + x, "/%s%s", node->name, keys);
		}
	}

cleanup:
	ly_set_free(set);
	free(keys);
	return xpath;
}

static char *lypy_node_fullname(const struct lys_node *node)
{
	const struct lys_module *module;
	char *fullname = NULL;

	module = lys_node_module(node);
	if (!module)
		return NULL;

	if (asprintf(&fullname, "%s:%s", module->name, node->name) < 0)
		return NULL;

	return fullname;
}

const struct lyd_node *lypy_get_root_node(const struct lyd_node *node) {
  const struct lyd_node *tmp_node = NULL;
	tmp_node = node;
  while(1){
		if(!tmp_node->parent){
			return tmp_node;
		}
		tmp_node = tmp_node->parent;
  }

}

int validate_data_tree(struct lyd_node *node, struct ly_ctx *ctx){
	struct lyd_node *ptr = node;
	int response = 0;
	response = lyd_validate(&ptr, LYD_OPT_DATA_NO_YANGLIB | LYD_OPT_STRICT, ctx);
	return response;
}

int lypy_process_attributes(struct lyd_node *root, struct ly_ctx *ctx, struct lyd_node *tempRoot)
{
	struct lyd_node *elem, *next, *toreplace = lyd_dup(tempRoot, LYD_DUP_OPT_RECURSIVE | LYD_DUP_OPT_NO_ATTR);
	struct lyd_attr *node_attr;
	struct ly_set *nodes_to_remove = ly_set_new();
	char *node_xpath;
	char *list_xpath = NULL;
	short mergeReplacement = 0;

	//Merge  the temp root into root. Then we can process the attributes as we have a final model
	lyd_merge(root, tempRoot, LYD_OPT_EXPLICIT);

	LY_TREE_DFS_BEGIN(tempRoot, next, elem) 
	{
		for (node_attr = elem->attr; node_attr; node_attr = node_attr->next) {
			if(strcmp(node_attr->name, "operation") == 0) {
				if(strcmp(node_attr->value_str, "remove") == 0) {
					node_xpath = lyd_path(elem);
					ly_set_merge(nodes_to_remove, lyd_find_path(root, node_xpath), 0);
					lyd_free(elem);
					elem = tempRoot;
				} else if (strcmp(node_attr->value_str, "replace") == 0) {
					if (elem->schema->nodetype == LYS_LIST) {
						const char *list_name = elem->schema->name;
						const char *list_parent_xpath = lyd_path(elem->parent);
						list_xpath = (char *) malloc(1 + strlen(list_parent_xpath) + strlen(list_name));
						sprintf(list_xpath, "/%s/%s", list_parent_xpath, list_name);
						node_xpath = list_xpath;
					} else
					{
						node_xpath = lyd_path(elem);
					}
					ly_set_merge(nodes_to_remove, lyd_find_path(root, node_xpath), 0);
					if(list_xpath != NULL) { free(list_xpath); };
					mergeReplacement = 1;
					lyd_free(elem);
					elem = tempRoot;
				}
			}
		}
        LY_TREE_DFS_END(tempRoot, next, elem);
	}
	
	for(unsigned int i = 0; i < nodes_to_remove->number; i++)
	{
		lyd_free(nodes_to_remove->set.d[i]);
	}
	
	if(mergeReplacement) { lyd_merge(root, toreplace, LYD_OPT_EXPLICIT | LYD_OPT_DESTRUCT); };

	ly_set_free(nodes_to_remove);

	lyd_free(tempRoot);

	return validate_data_tree(root, ctx);
}