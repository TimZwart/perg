# Perg

In the beginning, there was *grep*. What i used it for is mostly grep -r to find code. however this is extremely slow because grep -r searches literally everything. so we need a smarter search tool. 

tools like *ack*, *ag*, *ucg*, *ripgrep*, etc, are filling this gap. These are much smarter. However these suffer from problems as well: it is also hard to understand what they will search, what they won't search. and it is often difficult to learn how to do optimal search for your use case.

Perg is not really meant to be used as is. It is meant to provide inspiration on how to roll your own custom code search tool. it is not much harder than learning to use the other tools effectively. It is written in Python, not for performance reasons, but because it produces the shortest, clearest source code which is easy to understand and customize. It is also the tool i use daily and it is made mostly for my use case. if you want to have optimal results for you, you might have to make some changes.
