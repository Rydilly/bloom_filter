# bloom_filter
Small data structure project I made a while back.

When I taking ds&a I went on a tangent related to hashing. I really disliked the concept of tombstone hashing because it felt like I was redirecting an issue hoping it would resolve it's self later via a put hashing to the respective cluster. If the user use case was a series of puts deletes then contains the tombstones would never be resolved and carry a fractional toll at each hash leading to the respective buffer slot cluster. Although improbable with a use that puts and deletes in random sequence, running a hash that has the possibility of devolving asymptotic lookup complexity to O(n) left a bad taste in my mouth. This is the first of three programs in a journey of mine to make something more robust.

What is a bloom filter- A bloom filter is a filter not a hash meaning its purpose is to know if an item has not been stored to the filter or if there is a CHANCE it could have been. 

How does it work?- when a value is added to a filter, it is assigned 2 hashes which can be used to create an infinite number of statistically unique hashes using the double hashing trick: hash1 + i * hash2. a number of hashes are made based on percision and expected items. Every hash is a bit, when accessed it is turned to 1(true) it not already.
Because of this every item has a somewhat unique finger print of several hashes. When it is time to check if an item is in the filter, the items respective hashes are recalculated and respective buffer slots are checked. If any are 0 that means the item has certainly never been put into the filter. If all slots accessed are 1 there are 2 possibilities, Either the item has been put in the filter or multiple items finger prints happen to plot to the same slots resulting in a false positive.
A buffer is made based on the number of expected elements and percision aka how confident you want a positive result to be. As the buffer size grows or the total number of items going in shrinks, there is a decreased likelyhood of finger print collisions or false positives. The inverse decreases certainty.

How does this corelate to hashing- bloom filtering is a simple project to learn about the benefits of running multiple hash functions on a singular item. 

How to use?-
make a filter:
f=bloom_filter(
    precision=#how confident do you want to be in positive results with the trade off of space
    expected_size=#how many items you plan to put in the filter(note precision cannot be ensured if actual_size>expected_size)
)

add an item:
f.add(item)

see if an item is certainly not in the filter or (percision) likely to be in the filter:
f.contains(item)

What did I learn?:
After this project I became an advocate of ds&a curriculum including filters. they should suffice as a good intoduction into hashing while also holding benefits in cache locality. since a buffer slot was a single bit the total space of the buffer was tiny and lookup was incredible compared to hashing due to cpu cache line restrictions.

When to not use a filter?
Although the are incredibly efficent in space and time their use cases are somewhat limmited. Not knowing if an item is certainly in the filter due to false positives.Being unable to delete because a buffer slot may be shared between 2 items are the main downsides. 




