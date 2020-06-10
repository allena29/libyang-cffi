

#include <stdio.h>
#include <stdlib.h>
#include "libyang.h"

int main(void)
{
  printf("Repro Test 1\n");

  struct ly_ctx *ctx;
  struct lyd_node *dt;

  ctx = ly_ctx_new(NULL, 0);
  ly_ctx_set_searchdir(ctx, "yang");
  ly_ctx_load_module(ctx, "repro", NULL);
  printf("repro yang module loaded\n");
  printf("end repro test1\n");

  struct lyd_node *root_node;
  struct lyd_node *data_node;
  struct ly_set *results;
  root_node = lyd_new_path(NULL, ctx, "/repro:tarzan", "A", 0, LYD_PATH_OPT_UPDATE);
  if (root_node==NULL) {
    printf("Unable to set value for tarzan to A - empty data tree\n");
    exit(1);
  }
  
  data_node = lyd_new_path(root_node, ctx, "/repro:tarzan", "Z", 0, LYD_PATH_OPT_UPDATE);
  if (data_node==NULL) {
    printf("   EXPECTED Unable to set value for tarzan to Z- it's an invalid value so this is good.\n");
  }

 
  results = lyd_find_path(root_node, "/repro:tarzan");
  printf("We have the following number of results... %u", results->number);
  printf("\n");


  struct lyd_node_leaf_list *leaf;
  leaf = results->set.d[0];
  printf("TARZAN is %s\n", leaf->value_str);


   lyd_print_file(stdout, root_node, 1, LYP_WITHSIBLINGS);

}

