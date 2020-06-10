# lyd_new_path returns a lyd_node when set with an invalid value.

- `/repro:tarzan` is an enumeration with A, B, C as valid values

- We create the data tree by setting `/repro:tarzan` to A and get a lyd\_node back

- We set the path `/repro:tarzan` to Z and do not get a lyd\_node back, the update should not
  have happened because it doesn't match the enumeration and we see `libyang[0]: Invalid value "Z" in "tarzan" element. (path: /repro:tarzan)`

- We query the path with `lyd_find_path` and get back 1 result with the value `Z`.

- `lyd_print_file` dumps out the data tree with Z.



# Execute

```
gcc -I/usr/local/include/libyang -lyang test4.c && ./a.out
```


# Output Example

```
Repro Test 1
repro yang module loaded
end repro test1
libyang[0]: Invalid value "Z" in "tarzan" element. (path: /repro:tarzan)
   EXPECTED Unable to set value for tarzan to Z- it's an invalid value so this is good.
We have the following number of results... 1
TARZAN is A
<tarzan xmlns="http://example.com/repro">A</tarzan>
```
