import sys

print(f"{'='*30}\nReference Counting Demo\n{'='*30}\na_list = [1,2,3]\nb_list = a_list\n")

a_list = [1, 2, 3]
print(f"Initialize : a_list: {a_list}")
b_list = a_list
print(f"Assigned : b_list = a_list")
print(f"Address of a_list: {hex(id(a_list))}")
input()
print(f"Address of b_list: {hex(id(b_list))}")
print("Both addresses are the same, so both variables point to the same object.\n")

a_list[0] = 0
print("After modifying a_list[0]=0")
input()
print("b_list:", b_list)
print("a_list:", a_list)
print("Both reflect the change, confirming they are the same object.\n")

input()

# Show reference count using sys.getrefcount (the correct way)
print("=" * 50)
print("Reference Counting with sys.getrefcount()")
print("=" * 50)

refcount_1 = sys.getrefcount(a_list)
print(f"\nRefcount of a_list: {refcount_1}")

# Create another reference
c_list = a_list
refcount_2 = sys.getrefcount(a_list)
print(f"After c_list = a_list, refcount: {refcount_2}")

# Delete a reference
del c_list
refcount_3 = sys.getrefcount(a_list)
print(f"After del c_list, refcount: {refcount_3}")

print("\nNote: sys.getrefcount() returns one higher than expected because")
print("the argument itself is also referenced during the function call.")
print("\nRefcount breakdown:")
print("  - a_list variable: +1")
print("  - b_list variable: +1")
print("  - sys.getrefcount() argument: +1 (temporary)")
print(f"  Total: {refcount_3} (includes the function call reference)")

#print(ctypes.c_long.from_address(id(a)).value) # this didnt work, likely due to optimizations in Python 3.10+ that hide the reference count field