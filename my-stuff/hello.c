#include <stdio.h>
#include "libyang.h"

struct ly_ctx *ctx = NULL;
struct lyd_node *root_a = NULL;
struct lyd_node *root_b = NULL;
struct lyd_difflist *diff;
char *str; // * means dereference

int main()
{
   // printf() displays the string inside quotation
   printf("Hello, World!\n");
   char* yang_folder = NULL;
   yang_folder = "/Users/adam/python-yang-voodoo/yang";

   printf("Yang Location: %s", yang_folder);
   printf("\n");
   ctx = ly_ctx_new(yang_folder, 0);


   ly_ctx_load_module(ctx, "integrationtest", NULL);
   printf("Loaded yang module to ctx\n");


   root_a = lyd_new_path(NULL, ctx, "/integrationtest:simpleleaf","a", 0, 0);
   root_a = lyd_new_path(root_a, NULL, "/integrationtest:simpleenum","A", 0, 0);
   root_b = lyd_new_path(NULL, ctx, "/integrationtest:simpleleaf","b", 0, 0);
   //lyd_new_path(NULL, ctx2, "/integrationtest:simpleleaf", "B", 0, 0);

   diff = lyd_diff(root_a, root_b, 0);
   size_t diff_size = sizeof(diff);
   uint64_t i;
   printf("Got a diffresult (%d)\n", diff_size);
   for(i=0; i<diff_size; i++){
     printf("\n   Diff result %i\n", i);
    //see: test_diff2(void **state)

     //printf((str = lyd_path(diff->first[i])));
     //printf("%s",diff[i]);
   }
// we can serialise into xml/json  - probably
///   https://netopeer.liberouter.org/doc/libyang/master/group__datatree.html#ga5dee9dd41c57edc1fc2185f6a2c233a3
   return 0;
}
