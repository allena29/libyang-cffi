#include <stdio.h>
#include "libyang.h"

struct ly_ctx *ctx = NULL;

int main()
{
   // printf() displays the string inside quotation
   printf("Hello, World!");
   char* yang_folder = NULL;
   yang_folder = "/Users/adam/python-yang-voodoo/yang";

   printf("Yang Location: %s", yang_folder);
   ctx = ly_ctx_new(yang_folder, 0);
   return 0;
}
