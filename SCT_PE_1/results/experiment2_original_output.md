Binary Search Explained
Binary search is an efficient searching algorithm used to find a target element in a sorted array. Instead of checking every element one by one, it repeatedly divides the search range into half.

Example
Suppose we have a sorted array:

10 20 30 40 50 60 70

Target element: 40

Step-by-step process

1-Find the middle element
Middle element is 40. Since 40 equals the target, the element is found immediately.

2-If the middle element is not the target
- If the target is smaller, search the left half.
- If the target is larger, search the right half.

3-Repeat until found
Continue halving the remaining range until the target is found or no elements remain.   


Python implementation...

def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


numbers = [10, 20, 30, 40, 50, 60, 70]
print(binary_search(numbers, 50))

Output-4