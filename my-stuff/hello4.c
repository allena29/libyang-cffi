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
   yang_folder = "/Users/adam/python-yang-voodoo/yang";

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
   lyd_new_path(root_a, NULL, "/integrationtest:simpleenum","A", 0, 0);
   lyd_new_path(root_a, NULL, "/integrationtest:validator/mandatories","", 0, 0);

   //root_a = lyd_new_path(NULL, ctx, "/integrationtest:simpleenum","A", 0, 0);
   lyd_new_path(root_a, NULL, "/integrationtest:simplelist[simplekey='A']/simplekey","A" , 0, 0);
   lyd_new_path(root_a, NULL, "/integrationtest:simplelist[simplekey='B']/simplekey","B" , 0, 0);
   lyd_new_path(root_a, NULL, "/integrationtest:simplelist[simplekey='B']/nonleafkey", "4444" , 0, 0);

   lyd_new_path(root_a, NULL, "/integrationtest:simplelist[simplekey='C']/simplekey","C" , 0, 0);
   lyd_new_path(root_a, NULL, "/integrationtest:simplelist[simplekey='D']/simplekey","D" , 0, 0);
   //lyd_new_path(root_a, NULL, "/integrationtest:simpleenum","A", 0, 0);
   root_b = lyd_new_path(NULL, ctx, "/integrationtest:simpleleaf","b", 0, 0);
   lyd_new_path(root_b, NULL, "/integrationtest:bronze/silver/gold/platinum/deep","in a cavern", 0, 0);
   lyd_new_path(root_b, NULL, "/integrationtest:container-and-lists/multi-key-list[A='a'][B='b']/inner/C", "c", 0, 0);
   lyd_new_path(root_b, NULL, "/integrationtest:container-and-lists/multi-key-list[A='aa'][B='bb']/inner/C", "cc", 0, 0);
   /*
   int 	lyd_change_leaf (struct lyd_node_leaf_list *leaf, const char *val_str)
 	Change value of a leaf node. More...

  struct lyd_node * 	lyd_new_anydata (struct lyd_node *parent, const struct lys_module *module, const char *name, void *value, LYD_ANYDATA_VALUETYPE value_type)
 	Create a new anydata or anyxml node in a data tree. More...

  */
  uint8_t response = 4;
  printf("\naddres sif iisis %p", &response);
  uint8_t *ptr_to_response = &response;
  printf("\nnon-point version %d", response);
  printf("\npoint version %p", ptr_to_response);
  printf("\npoint version %p (address of pointer)", &ptr_to_response);
  printf("\npoint version %i (derfernece)", *ptr_to_response);

 // * is declaring a pointer or defrencing,, or a derferecning
  uint8_t **double_ptr = &ptr_to_response;
  printf("\nDouble prt's address %p", &double_ptr);
  printf("\nGuess..... %i", *(*double_ptr) );
  printf("\n");
  printf("\nValue of &n is : %p", &root_a);
  printf("\n...");
  //printf("%d", root_a);

  //root_a is 'struct lyd_node *


  //response = lyd_validate(&root_a, LYD_OPT_CONFIG, NULL);

// make it valid
  //lyd_new_path(root_a, NULL, "/integrationtest:validator/mandatories/this-is-mandatory","SATISFIED?", 0, 0);
  struct lyd_node **ptr_node;
  struct lyd_node **ptr_nodex = &root_a;
  response = lyd_validate(ptr_nodex, LYD_OPT_CONFIG, NULL);

  printf("Response to validation.... %d\n", response);
   return 0;
}
