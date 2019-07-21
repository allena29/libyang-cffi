# Pure C

 ```bash
 gcc -Wall -g -o hello hello.c -lyang -I /usr/local/include/libyang/ && ./hello
 ```

# CFFI

This gets run to build the libraries

```python
import cffi


HERE = os.path.dirname(__file__)
BUILDER = cffi.FFI()
with open(os.path.join(HERE, 'cdefs.h')) as f:
    BUILDER.cdef(f.read())
with open(os.path.join(HERE, 'source.c')) as f:
    BUILDER.set_source('_libyang', f.read(), libraries=['yang'],
                       extra_compile_args=['-Werror', '-std=c99'],
                       py_limited_api=False)

if __name__ == '__main__':
    BUILDER.compile()

```

# Changing libyang-cffi bindings

- Add a new function to cffi (not sure how this kicks in)

```
static char *adams(){
	char *fullname = "adam";
	return fullname;
}
```

# Updating cdefs

```
char *adams();
```

# Rebuilding libyang-cffi bindings

```
env LIBYANG_INSTALL=system python3 setup.py install
```


# Running from python

```python

class Data(object):

    def __init__(self, ctx):
        self._ctx = print(ctx)
        self.root_a = None
        self.root_b = None

        print("Libyang initialised with a ctx")

    def set_data_by_xpath(self, path, value):
        x=c2str(lib.adams())
        print(x)

        
```
