

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
  root_node = lyd_new_path(NULL, ctx, "/repro:bob", "1004", 0, LYD_PATH_OPT_UPDATE);
  if (root_node==NULL) {
    printf("Unable to set value for bob to 1004 - empty data tree\n");
    exit(1);
  }
  
  data_node = lyd_new_path(root_node, ctx, "/repro:bob", "1005", 0, LYD_PATH_OPT_UPDATE);
  if (data_node==NULL) {
    printf("Unable to set value for bob to 1005 - existing data tree\n");
    exit(1);
  }

  data_node = lyd_new_path(root_node, ctx, "/repro:bob", "1005", 0, LYD_PATH_OPT_UPDATE);
  if (data_node==NULL) {
    printf("  EXPECTED Unable to set value for bob to 1005 - existing data tree\n");
    printf("  we only get data_node returned if the update happened... here we don't change the value\n");
  }
 
  results = lyd_find_path(root_node, "/repro:bob");
  printf("We have the following number of results... %u", results->number);
  printf("\n");


}

