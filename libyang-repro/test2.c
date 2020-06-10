

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
  root_node = lyd_new_path(NULL, ctx, "/repro:bob", "fred", 0, LYD_PATH_OPT_UPDATE);
  if (root_node==NULL) {
    printf("Unable to set value for bob to FRED - empty data tree\n");
    printf("We required this to fail -- so happy that it did\n");
    exit(0);
  }
  
  exit(1);

}

