Binary Search — Beginner-Friendly Explanation
Binary search is a searching method that finds an element in a sorted array by repeatedly dividing the search space into half.

Imagine looking for a word in a dictionary. Instead of reading every word from the beginning, you open near the middle and decide which half to search. Binary search works the same way.
1. Example: Find 16
Our sorted array is:
2 0 5 1 8 2 12 3 16 4 23 5 38 6

Numbers are above; array indices are below. We want to find 16.

We use three variables:
- low — index of the first element in the current search range.
- high — index of the last element in the current search range.
- mid — index of the middle element.
2. Step-by-step search
Step 1: Check the middle
Compare

2 5 8 12 16 23 38


- low = 0, high = 6
- mid = (0 + 6) // 2 = 3
- Middle element = 12
- Since 16 > 12, search the right half.
  
  Why eliminate half? The array is sorted, so every element to the left of 12 is smaller than 12 and therefore cannot be 16.

Step 2: Search the right half
2 5 8 12 16 23 38

- low = 4, high = 6
- mid = (4 + 6) // 2 = 5
- Middle element = 23
- Since 16 < 23, search the left part of this range.
  
  Why eliminate half? The elements to the right of 23 are larger than 23, so they cannot be 16.

Step 3: Find the target

Found
2 5 8 12 16 23 38

- low = 4, high = 4
- mid = (4 + 4) // 2 = 4
- Middle element = 16
- Target equals the middle element. Found at index 4!

3. Pseudocode

BINARY_SEARCH(array, target):
    low = 0
    high = length(array) - 1

    WHILE low <= high:
        mid = (low + high) // 2

        IF array[mid] == target:
            RETURN mid

        ELSE IF array[mid] < target:
            low = mid + 1

        ELSE:
            high = mid - 1

    RETURN -1


- Return the index if the target is found.
- Return -1 if the target does not exist in the array.
- // means integer division, which discards the fractional part.


4. Time complexity
Case	Time complexity	Meaning
Best case	\(O(1)\)	The first middle element is the target.
Average case	\(O(\log n)\)	The search repeatedly halves the range.
Worst case	\(O(\log n)\)	It keeps halving until the target is found or the range is empty.

For example, with 1,000 elements, binary search needs at most about 10 comparisons to narrow the search to one element.

Important: Binary search requires the input array to be sorted. If the array is unsorted, its left/right elimination logic is not reliable.

Remember: Compare the middle, discard the impossible half, and repeat until you find the target.
