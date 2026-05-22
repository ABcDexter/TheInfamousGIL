import sys
import ctypes

print(f"{'='*30}\nReference Counting Demo\n{'='*30}\na_list = [1,2,3]\nb_list = a_list\n")

a_list = [1, 2, 3]
b_list = a_list

print(f"Address of a_list: {hex(id(a_list))}")
print(f"Address of b_list: {hex(id(b_list))}")
print("Both addresses are the same, so both variables point to the same object.\n")

a_list[0] = 0
print("After modifying a_list[0]:")
print("b_list:", b_list)
print("a_list:", a_list)
print("Both reflect the change, confirming they are the same object.\n")

# Show reference count using ctypes (CPython-specific)
refcount_ctypes = ctypes.c_long.from_address(id(a_list)).value
print(f"Reference count of a_list (via ctypes): {refcount_ctypes}")

# Show reference count using sys.getrefcount
refcount_sys = sys.getrefcount(a_list)
print(f"Reference count of a_list (via sys.getrefcount): {refcount_sys}")
print("\nNote: sys.getrefcount() returns one higher than expected because the argument is also referenced by the function call itself.")