# bloom_filter

When I was taking DS&A I went on a tangent related to hashing. I really disliked the concept of tombstone hashing because it felt like I was redirecting an issue and hoping it would resolve itself later via a put hashing to the respective cluster containing a tombstone. If the user use case was a series of puts and deletes followed by contains, the tombstones would never be resolved and would carry a fractional toll at each lookup leading to the respective cluster. Although improbable with a use case of puts and deletes in random sequence, running a hash that has the possibility of devolving asymptotic lookup complexity to O(n) left a bad taste in my mouth. This is the first of three programs in a journey of mine to make something more robust. Bloom filtering is a simple project to learn about the benefits of running multiple hash functions on a singular item. Bloom filters got me comfortable with multiple hash functions which I will utilize on in my next project, [Cuckoo Hashing](https://github.com/Rydilly/Cuckoo_Hashing).

## What is a bloom filter?

A bloom filter is a filter, not a hash — meaning its purpose is to know if an item has *not* been stored to the filter, or if there is a *chance* it could have been.

## How does it work?

When a value is added to a filter, it is assigned 2 hashes which can be used to create an infinite number of statistically unique hashes using the double hashing trick: `hash1 + i * hash2`. A number of hashes are made based on precision and expected items. Every hash points to a bit; when accessed, it is turned to 1 (true) if not already.

Because of this, every item has a somewhat unique fingerprint of several hashes. When it is time to check if an item is in the filter, the item's respective hashes are recalculated and respective buffer slots are checked. If any are 0, that means the item has certainly never been put into the filter. If all slots accessed are 1, there are 2 possibilities: either the item has been put in the filter, or multiple items' fingerprints happen to plot to the same slots, resulting in a false positive.

A buffer is made based on the number of expected elements and precision — aka how confident you want a positive result to be. As the buffer size grows or the total number of items going in shrinks, there is a decreased likelihood of fingerprint collisions or false positives. The inverse decreases certainty.


## Does it actually work?

Running the demo across a few configurations:

| n         | target p | m (bits)  | k  | size     | empirical p |
| --------- | -------- | --------- | -- | -------- | ----------- |
| 10,000    | 10%      | 47,926    | 3  | 5.9 KB   | 10.08%      |
| 10,000    | 1%       | 95,851    | 7  | 11.7 KB  | 0.98%       |
| 10,000    | 0.1%     | 143,776   | 10 | 17.6 KB  | 0.11%       |
| 100,000   | 1%       | 958,506   | 7  | 117.0 KB | 1.00%       |
| 1,000,000 | 1%       | 9,585,059 | 7  | 1.14 MB  | 1.00%       |

A million items in ~1 MB with a 1% target false positive rate that lands at 1.0001% empirically.

For each row I insert `n` distinct integers into the filter, then query it with the first `10n` integers and count how many of the `9n` known-negatives come back as positives.

## The math

The whole thing hinges on picking two numbers: `m` (buffer size in bits) and `k` (hashes per item), given `n` (expected items) and `p` (target false positive rate). Here's how I worked it out.

Probability a given slot is *not* flipped by one hash: $1 - \frac{1}{m}$

After inserting $n$ items each flipping $k$ bits, the probability a given slot is still 0:

$$\left(1 - \frac{1}{m}\right)^{nk}$$

Using $\lim_{x \to \infty} \left(1 - \frac{1}{x}\right)^x = \frac{1}{e}$ this approximates to $e^{-nk/m}$ for large $m$.

So the probability a slot *is* set is $1 - e^{-nk/m}$, and the false positive rate — all $k$ slots for a query happening to be set — is:

$$p = \left(1 - e^{-nk/m}\right)^k$$

To minimize $p$ over $k$, take $\frac{d(\ln p)}{dk} = 0$. The optimum lands at:

$$e^{-nk/m} = \frac{1}{2}$$

which is the same as saying **the filter is optimal when exactly half the bits are set** — a really pretty result.

Substituting back gives $p = (1/2)^k$, and rearranging:

$$k = -\frac{\ln p}{\ln 2}, \qquad m = -\frac{n \ln p}{(\ln 2)^2}$$

Those are the two formulas that show up in `_calc_slots` and `__init__` — the whole thing falls out of "keep the buffer half full." (For the raw scratch derivation with all the tired algebra intact, see the docstring at the top of `bloom_filter.py`.)



## How to use?

Requirements: `mmh3`, `bitarray`.

Make a filter:

```python
f = bloom_filter(
    precision=...,     # how confident you want to be in positive results, with the trade off of space
    expected_size=..., # how many items you plan to put in the filter
                       # (note: precision cannot be ensured if actual_size > expected_size)
)
```

Add an item:

```python
f.add(item)
```

See if an item is certainly not in the filter, or possibly in it (with false positive rate precision):

```python
f.contains(item)
```

`add` and `contains` currently accept `int` or `str` keys.

Running `bloom_filter.py` directly runs the demo used to generate the table above.

## What did I learn?

After this project I became an advocate of DS&A curriculum including filters. They should suffice as a good introduction into hashing while also holding benefits in cache locality. Since a buffer slot was a single bit, the total space of the buffer was tiny and lookup was incredible compared to hashing due to CPU cache line restrictions.

## When to not use a filter?

Although they are incredibly efficient in space and time, their use cases are somewhat limited. Not knowing if an item is certainly in the filter due to false positives, and being unable to delete because a buffer slot may be shared between 2 items, are the main downsides. Items also do not contain data connected to them, a filter's only purpose is to reject items that are certainly not in it.