"""leetcode.py -- Medium-difficulty interview problems, grouped by technique.

Companion to prelude.py, drilled by leetcode-trainer.el instead of fpython-trainer.el.
Where prelude.py teaches the vocabulary, this file drills the techniques interviewers
actually probe for: hash maps, two pointers, sliding window, binary search on the answer
space, BFS/DFS, backtracking, DP, intervals, heaps. LeetCode tags most of these problems
Medium -- the sweet spot for FAANG-style interviews: one or two non-obvious insights,
20-35 minutes for a prepared candidate, usually turning an O(n^2) brute force into
O(n) or O(n log n). A few (partition_k_subsets, word_ladder) are officially Hard but
sit right at the edge and reuse techniques drilled elsewhere in the file.

Within a section, problems run in roughly increasing difficulty. Solutions favor the
idiomatic interview answer over cleverness -- what you'd actually write on a whiteboard.

    ListNode / TreeNode: the two LeetCode-standard node shapes, same as prelude.py's.
"""

import heapq
from collections import deque, defaultdict, Counter

# ============ 1. arrays & hashing ============

def two_sum(nums, target):                  # index pair summing to target, O(n)
    seen = {}                                # value -> index seen so far
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []

def group_anagrams(words):                   # bucket by sorted-letters key
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)
    return list(groups.values())

def top_k_frequent(nums, k):                 # bucket sort by count, O(n)
    counts = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for x, c in counts.items():
        buckets[c].append(x)
    out = []
    for c in range(len(buckets) - 1, 0, -1):
        for x in buckets[c]:
            out.append(x)
            if len(out) == k:
                return out
    return out

def product_except_self(nums):               # no division, two passes
    n = len(nums)
    out = [1] * n
    left = 1
    for i in range(n):
        out[i] = left
        left *= nums[i]
    right = 1
    for i in range(n - 1, -1, -1):
        out[i] *= right
        right *= nums[i]
    return out

def longest_consecutive(nums):               # O(n): only start counting at run starts
    present = set(nums)
    best = 0
    for x in present:
        if x - 1 in present:
            continue
        length = 1
        while x + length in present:
            length += 1
        best = max(best, length)
    return best

# ============ 2. two pointers ============

def is_palindrome_alnum(s):                  # ignore case & non-alnum, close from both ends
    i, j = 0, len(s) - 1
    while i < j:
        while i < j and not s[i].isalnum():
            i += 1
        while i < j and not s[j].isalnum():
            j -= 1
        if s[i].lower() != s[j].lower():
            return False
        i, j = i + 1, j - 1
    return True

def three_sum(nums):                         # sort, fix one, two-pointer the rest
    nums.sort()
    out = []
    for i, x in enumerate(nums):
        if i > 0 and x == nums[i - 1]:
            continue
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            total = x + nums[lo] + nums[hi]
            if total < 0:
                lo += 1
            elif total > 0:
                hi -= 1
            else:
                out.append([x, nums[lo], nums[hi]])
                lo += 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
    return out

def container_with_most_water(heights):      # move the shorter wall inward
    lo, hi, best = 0, len(heights) - 1, 0
    while lo < hi:
        best = max(best, (hi - lo) * min(heights[lo], heights[hi]))
        if heights[lo] < heights[hi]:
            lo += 1
        else:
            hi -= 1
    return best

def trap_rain_water(heights):                # running max from each side, O(n) O(1)
    lo, hi = 0, len(heights) - 1
    left_max, right_max, water = 0, 0, 0
    while lo < hi:
        if heights[lo] < heights[hi]:
            left_max = max(left_max, heights[lo])
            water += left_max - heights[lo]
            lo += 1
        else:
            right_max = max(right_max, heights[hi])
            water += right_max - heights[hi]
            hi -= 1
    return water

# ============ 3. sliding window ============

def longest_substring_no_repeat(s):           # window shrinks past the last duplicate
    last_seen, start, best = {}, 0, 0
    for i, c in enumerate(s):
        if c in last_seen and last_seen[c] >= start:
            start = last_seen[c] + 1
        last_seen[c] = i
        best = max(best, i - start + 1)
    return best

def min_window_substring(s, t):               # shrink while still covering all of t
    need = Counter(t)
    missing = len(t)
    start, end = 0, 0
    lo = 0
    for hi, c in enumerate(s, 1):
        if need[c] > 0:
            missing -= 1
        need[c] -= 1
        while missing == 0:
            if end == 0 or hi - lo < end - start:
                start, end = lo, hi
            need[s[lo]] += 1
            if need[s[lo]] > 0:
                missing += 1
            lo += 1
    return s[start:end]

def max_sliding_window(nums, k):              # monotonic deque of candidate indices
    dq, out = deque(), []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

def longest_repeating_replacement(s, k):      # window valid while (len - max count) <= k
    counts = Counter()
    start, best, max_count = 0, 0, 0
    for end, c in enumerate(s):
        counts[c] += 1
        max_count = max(max_count, counts[c])
        while (end - start + 1) - max_count > k:
            counts[s[start]] -= 1
            start += 1
        best = max(best, end - start + 1)
    return best

# ============ 4. stacks & queues ============

def is_valid_parens(s):                       # push opens, match closes against the top
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for c in s:
        if c in pairs:
            if not stack or stack.pop() != pairs[c]:
                return False
        else:
            stack.append(c)
    return not stack

def eval_rpn(tokens):                          # classic stack machine
    ops = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
           "*": lambda a, b: a * b, "/": lambda a, b: int(a / b)}
    stack = []
    for tok in tokens:
        if tok in ops:
            b, a = stack.pop(), stack.pop()
            stack.append(ops[tok](a, b))
        else:
            stack.append(int(tok))
    return stack[0]

def daily_temperatures(temps):                 # monotonic decreasing stack of indices
    out = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            out[j] = i - j
        stack.append(i)
    return out

class MinStack:                                 # push/pop/top/get_min, all O(1)
    def __init__(self):
        self.stack = []
        self.mins = []
    def push(self, x):
        self.stack.append(x)
        self.mins.append(x if not self.mins else min(x, self.mins[-1]))
    def pop(self):
        self.mins.pop()
        return self.stack.pop()
    def top(self):
        return self.stack[-1]
    def get_min(self):
        return self.mins[-1]

# ============ 5. binary search ============

def search_rotated(nums, target):               # one half is always sorted; pick it
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1

def find_min_rotated(nums):                     # binary search for the pivot
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]

def koko_eating_bananas(piles, h):              # binary search on the answer: min speed
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        hours = sum((p + mid - 1) // mid for p in piles)
        if hours <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo

def find_peak_element(nums):                    # climb toward the higher neighbor
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[mid + 1]:
            hi = mid
        else:
            lo = mid + 1
    return lo

# ============ 6. linked lists ============

class ListNode:                                  # the LeetCode linked list
    def __init__(self, val=0, nxt=None):
        self.val, self.next = val, nxt

def reverse_list(head):                          # rewire pointers one node at a time
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next
    return prev

def merge_two_lists(a, b):                       # splice the smaller head forward
    dummy = tail = ListNode()
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next

def remove_nth_from_end(head, n):                # two pointers, n apart
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n):
        fast = fast.next
    while fast.next:
        fast, slow = fast.next, slow.next
    slow.next = slow.next.next
    return dummy.next

def reorder_list(head):                          # find middle, reverse back half, zip
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    second = reverse_list(slow)
    first = head
    while second.next:
        first.next, first = second, first.next
        second.next, second = first, second.next
    return head

# ============ 7. trees ============

class TreeNode:                                  # the LeetCode binary tree
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def max_depth(root):                             # depth-first, recursive
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

def is_valid_bst(root):                           # carry the open range downward
    def valid(node, lo, hi):
        if node is None:
            return True
        if not (lo < node.val < hi):
            return False
        return valid(node.left, lo, node.val) and valid(node.right, node.val, hi)
    return valid(root, float("-inf"), float("inf"))

def level_order(root):                            # BFS, one list per depth
    out, q = [], deque([root] if root else [])
    while q:
        level = []
        for _ in range(len(q)):
            node = q.popleft()
            level.append(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        out.append(level)
    return out

def lowest_common_ancestor(root, p, q):           # split point: p and q on opposite sides
    node = root
    while node:
        if p.val < node.val and q.val < node.val:
            node = node.left
        elif p.val > node.val and q.val > node.val:
            node = node.right
        else:
            return node
    return None

def build_from_preorder_inorder(preorder, inorder):   # recursive split on the root
    idx = {val: i for i, val in enumerate(inorder)}
    def build(pre_lo, pre_hi, in_lo, in_hi):
        if pre_lo == pre_hi:
            return None
        root_val = preorder[pre_lo]
        mid = idx[root_val]
        left_size = mid - in_lo
        node = TreeNode(root_val)
        node.left = build(pre_lo + 1, pre_lo + 1 + left_size, in_lo, mid)
        node.right = build(pre_lo + 1 + left_size, pre_hi, mid + 1, in_hi)
        return node
    return build(0, len(preorder), 0, len(inorder))

# ============ 8. graphs ============

def num_islands(grid):                            # DFS-flood each unvisited land cell
    rows, cols = len(grid), len(grid[0])
    def sink(r, c):
        if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != "1":
            return
        grid[r][c] = "0"
        sink(r + 1, c); sink(r - 1, c); sink(r, c + 1); sink(r, c - 1)
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                sink(r, c)
    return count

def course_schedule(num_courses, prereqs):        # cycle detection via Kahn's topo sort
    indeg = [0] * num_courses
    adj = defaultdict(list)
    for a, b in prereqs:
        adj[b].append(a)
        indeg[a] += 1
    q = deque(c for c in range(num_courses) if indeg[c] == 0)
    seen = 0
    while q:
        c = q.popleft()
        seen += 1
        for nxt in adj[c]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
    return seen == num_courses

def clone_graph(node):                            # BFS with an old-node -> clone map
    if node is None:
        return None
    clones = {node: type(node)(node.val)}
    q = deque([node])
    while q:
        cur = q.popleft()
        for nbr in cur.neighbors:
            if nbr not in clones:
                clones[nbr] = type(nbr)(nbr.val)
                q.append(nbr)
            clones[cur].neighbors.append(clones[nbr])
    return clones[node]

def dijkstra(graph, source):                       # graph: node -> [(neighbor, weight)]
    dist = {source: 0}
    heap = [(0, source)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist.get(node, float("inf")):
            continue
        for nbr, w in graph.get(node, []):
            nd = d + w
            if nd < dist.get(nbr, float("inf")):
                dist[nbr] = nd
                heapq.heappush(heap, (nd, nbr))
    return dist

def word_ladder(begin, end, words):                 # BFS over one-letter-edit edges
    words = set(words)
    if end not in words:
        return 0
    q, seen = deque([(begin, 1)]), {begin}
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    while q:
        word, steps = q.popleft()
        if word == end:
            return steps
        for i in range(len(word)):
            for c in alphabet:
                cand = word[:i] + c + word[i + 1:]
                if cand in words and cand not in seen:
                    seen.add(cand)
                    q.append((cand, steps + 1))
    return 0

# ============ 9. backtracking ============

def subsets(nums):                                  # include/exclude each element
    out = []
    def go(i, cur):
        if i == len(nums):
            out.append(cur[:])
            return
        go(i + 1, cur)
        cur.append(nums[i])
        go(i + 1, cur)
        cur.pop()
    go(0, [])
    return out

def combination_sum(candidates, target):            # reuse allowed, prune on running sum
    out = []
    def go(start, remaining, cur):
        if remaining == 0:
            out.append(cur[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                continue
            cur.append(candidates[i])
            go(i, remaining - candidates[i], cur)
            cur.pop()
    go(0, target, [])
    return out

def permutations(nums):                              # swap-in-place, restore after
    out = []
    def go(k):
        if k == len(nums):
            out.append(nums[:])
            return
        for i in range(k, len(nums)):
            nums[k], nums[i] = nums[i], nums[k]
            go(k + 1)
            nums[k], nums[i] = nums[i], nums[k]
    go(0)
    return out

def word_search(board, word):                        # DFS with a visited marker, undo on backtrack
    rows, cols = len(board), len(board[0])
    def go(r, c, i):
        if i == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
            return False
        board[r][c] = "#"
        found = (go(r + 1, c, i + 1) or go(r - 1, c, i + 1) or
                 go(r, c + 1, i + 1) or go(r, c - 1, i + 1))
        board[r][c] = word[i]
        return found
    return any(go(r, c, 0) for r in range(rows) for c in range(cols))

def partition_k_subsets(nums, k):                     # Hard: bucket-fill with pruning
    total = sum(nums)
    if total % k:
        return False
    target = total // k
    nums.sort(reverse=True)
    if nums[0] > target:
        return False
    buckets = [0] * k
    def go(i):
        if i == len(nums):
            return True
        for b in range(k):
            if buckets[b] + nums[i] <= target:
                buckets[b] += nums[i]
                if go(i + 1):
                    return True
                buckets[b] -= nums[i]
            if buckets[b] == 0:
                break
        return False
    return go(0)

# ============ 10. dynamic programming ============

def coin_change(coins, amount):                       # bottom-up: fewest coins per amount
    dp = [0] + [float("inf")] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != float("inf") else -1

def longest_increasing_subsequence(nums):              # dp[i] = best subsequence ending at i
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp) if dp else 0

def edit_distance(a, b):                                # classic insert/delete/replace table
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[len(a)][len(b)]

def house_robber(nums):                                 # can't take two adjacent houses
    take, skip = 0, 0
    for x in nums:
        take, skip = skip + x, max(take, skip)
    return max(take, skip)

def unique_paths(rows, cols):                           # grid dp: sum of the two ways in
    dp = [1] * cols
    for _ in range(rows - 1):
        for c in range(1, cols):
            dp[c] += dp[c - 1]
    return dp[-1]

def zero_one_knapsack(weights, values, capacity):        # reverse-order 1D dp avoids reuse
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for cap in range(capacity, w - 1, -1):
            dp[cap] = max(dp[cap], dp[cap - w] + v)
    return dp[capacity]

# ============ 11. intervals ============

def merge_intervals(intervals):                          # sort, then fold overlapping runs
    intervals.sort(key=lambda iv: iv[0])
    out = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= out[-1][1]:
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return out

def insert_interval(intervals, new_interval):             # three phases: before, merge, after
    out, i, n = [], 0, len(intervals)
    while i < n and intervals[i][1] < new_interval[0]:
        out.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= new_interval[1]:
        new_interval = [min(new_interval[0], intervals[i][0]), max(new_interval[1], intervals[i][1])]
        i += 1
    out.append(new_interval)
    out.extend(intervals[i:])
    return out

def non_overlapping_intervals(intervals):                  # greedy: keep earliest end
    intervals.sort(key=lambda iv: iv[1])
    removed, prev_end = 0, float("-inf")
    for start, end in intervals:
        if start >= prev_end:
            prev_end = end
        else:
            removed += 1
    return removed

def meeting_rooms_needed(intervals):                        # sweep: sorted starts vs sorted ends
    starts = sorted(iv[0] for iv in intervals)
    ends = sorted(iv[1] for iv in intervals)
    rooms, end_ptr, peak = 0, 0, 0
    for s in starts:
        while end_ptr < len(ends) and ends[end_ptr] <= s:
            rooms -= 1
            end_ptr += 1
        rooms += 1
        peak = max(peak, rooms)
    return peak

# ============ 12. heaps ============

def kth_largest(nums, k):                                   # min-heap of size k
    heap = nums[:k]
    heapq.heapify(heap)
    for x in nums[k:]:
        if x > heap[0]:
            heapq.heapreplace(heap, x)
    return heap[0]

def k_closest_points(points, k):                             # max-heap of size k by -distance
    heap = []
    for x, y in points:
        dist = -(x * x + y * y)
        if len(heap) < k:
            heapq.heappush(heap, (dist, x, y))
        elif dist > heap[0][0]:
            heapq.heapreplace(heap, (dist, x, y))
    return [(x, y) for _, x, y in heap]

def task_scheduler(tasks, cooldown):                          # greedy from a max-heap of counts
    counts = list(Counter(tasks).values())
    heap = [-c for c in counts]
    heapq.heapify(heap)
    time = 0
    while heap:
        cycle, done = [], []
        for _ in range(cooldown + 1):
            if heap:
                done.append(-heapq.heappop(heap))
        for c in done:
            if c > 1:
                cycle.append(c - 1)
        time += (cooldown + 1) if heap or cycle else len(done)
        for c in cycle:
            heapq.heappush(heap, -c)
    return time

def find_median_stream(stream):                               # two heaps: lo (max) and hi (min)
    lo, hi, out = [], [], []
    for x in stream:
        heapq.heappush(lo, -x)
        heapq.heappush(hi, -heapq.heappop(lo))
        if len(hi) > len(lo):
            heapq.heappush(lo, -heapq.heappop(hi))
        out.append(-lo[0] if len(lo) > len(hi) else (-lo[0] + hi[0]) / 2)
    return out
