#include <stdio.h>
#include "libyang.h"

struct ly_ctx *ctx = NULL;
struct lyd_node *root_a = NULL;
struct lyd_node *root_b = NULL;
struct lyd_node *node = NULL;
struct lyd_difflist *diff;

int main()
{
   // printf() displays the string inside quotation
   printf("Hello, World!\n");
   char* yang_folder = NULL;
   yang_folder = "yang";

   printf("Yang Location: %s", yang_folder);
   printf("\n");
   ctx = ly_ctx_new(yang_folder, 0);


   ly_ctx_load_module(ctx, "integrationtest", NULL);
   printf("Loaded yang module to ctx\n");

   /*
   Documentation here:

   https://netopeer.liberouter.org/doc/libyang/master/group__datatree.html#ga470c3225f3f10666971723f8f9977a1a

   */
 root_a = lyd_new_path(NULL, ctx, "/integrationtest:simpleleaf","a", 0, 1);


  struct lyd_node *my_node;
  struct ly_set *my_set;
  const char *str;

  struct lyd_node_leaf_list my_leaf;


  my_set = lyd_find_path(root_a, "/integrationtest:simpleleaf");
  if(my_set == NULL){
    printf("my_set is null");
  }else{
    printf("my_set is not null");
    printf("my_set size: %d ", my_set->number);
    my_node = my_set->set.d[0];
    if(my_node == NULL){
      printf("my node is null!!!");
    }

    printf("\n");
    str = my_set->set.d[0]->schema->name;
    printf("sting : %s\n", str);
    if(my_set->set.d[0]->schema->nodetype & (LYS_LEAF | LYS_LEAFLIST)){
      printf("This is a leaf or a leaf list\n");
      my_node = my_set->set.d[0];
      my_leaf = *(struct lyd_node_leaf_list *)my_node;
      str = my_leaf.value_str;

      printf("string : %s\n", str);
    }



  }

   return 0;
}
