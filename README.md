I've come up with an idea for generating images, thoughts below. The main point: use probabilistic graphical models and parameter learning to generate images, and learn the parameters incrementally using user votes as a score function for candidates.

Some links of interest:
* http://www.cs.ubc.ca/~murphyk/Bayes/bnintro.html#learn
* https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers

A possible model for generating images: Draw triangles sequentially. Each subsequent triangle is directly connected to the previous triangle by some structure that we wish to learn. More generally, the structure connecting any two sequential triangles may be the same or different, but it will probably be simpler to assume they are the same. The observable random variables of triangles include vertex coordinates and rgb values. One may introduce other random variables which influence the CPDs of these fundamental observables.

The sequence terminates in an observable (tentatively) called "artiness". Observed artiness values are obtained by using the candidate model CPDs and structure to generate an image.

This requires a graph structure for triangle observables and for the relationship between sequential triangles. Reading a bit more, it may be desirable to try to learn structure. Is it possible to simulataneously learn structure and parameters?

Other things to do:
* Create an asycnhronous "watcher" to invoke functions.setNewBatch()
* Write an appropriate ImageGenerator._breed function.
* Fix up the index template (dynamically place things with jQuery, etc)

