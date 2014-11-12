I've come up with an idea for generating images, thoughts below. The main point: use probabilistic graphical models and parameter learning to generate images, and learn the parameters incrementally using user votes as a score function for candidates.

Some links of interest:
* http://www.cs.ubc.ca/~murphyk/Bayes/bnintro.html#learn
* https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers

A possible model for generating images: Draw triangles sequentially. Each subsequent triangle is directly connected to the previous triangle by some structure that we wish to learn. More generally, the structure connecting any two sequential triangles may be the same or different, but it will probably be simpler to assume they are the same. The observable random variables of triangles include vertex coordinates and rgb values. One may introduce other random variables which influence the CPDs of these fundamental observables.

The sequence terminates in an observable (tentatively) called "artiness". Observed artiness values are obtained by using the candidate model CPDs and structure to generate an image.

This requires a graph structure for triangle observables and for the relationship between sequential triangles. Reading a bit more, it may be desirable to try to learn structure. Is it possible to simulataneously learn structure and parameters?

------------------------------------------------

Bah! I wrote a detailed description of an approach to this problem, but a network error ate it. Briefly the idea is this:

1) Create a DAG for image generation that's a sequence of triangles terminating in a variable called artiness.
2) Use a DAG with known CPDs (either from a round of learning or some initialization) to generate a sequence of triangles (t1,..,tn) given a threshold artiness _a_ and a threshold probability _p_ that satisfy:
  2a) P(A>a | Tn=tn) > p, in otherwords given _a_ look for all possible _tn_ that satisfy the relation and pick one.
  2b) P(Tn=tn | Tn-1=tn-1) > p, again given _tn_ look for all possible _tn-1_ that satisfy the relation and pick one.
3) Users generate training data by scoring the artiness of a sequence of triangles.
4) Training data is used to learn CPDs and we return to step 2 to generate images and generate more training data. Rinse and repeat.

In other words, the objects we'll need are:
1) A DAG with associated CPDs and appropriate structure; call it an artist model or AM. AMs have the following methods:
  1a) Given a training set, the AM learns the most likely CPDs.
  1b) Given thresholds _a_ and _p_ described above, AM generates a sequence of triangles.
2) An image model (in the Django sense of models) with:
  2a) a sequence of triangles.
  2b) an artiness score.
3) A triangle model with:
  3a) vertex coordinates
  3b) rgb values
4) A training set object, which is really just a set of our image models.
