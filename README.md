Update 11/13
Okay, so below I had an idea for learning discrete CPDs in a Bayesian network, but my original idea of having completely general CPDs makes the problem size intractably large using a learning method called maximum likelihood estimation (MLE). Namely, general CPDs in this case need a huge number of training cases to get a good estimate of the true CPD. I could attack this in a few ways:

* Choose less general CPDs and learn parameters with MLE. This would mean coming up with parametric rules for how parent nodes influnce children, or even a set of distinct parametric rules that can be separately evaluated and the best one is retained. In order for this to be tractable, the size of the parameter space should be less than or equal to the number of training cases. I haven't estimated a reasonable number of training cases (since presumably it would depend on the rate of user input), but I'll just throw out 10,000. So I want to pick a scheme with a parameter space size less than 10,000, meaning the product of all the numbers of possible choices of all the parameters should be less than 10,000.
* Keep very general CPDs but learn them with a different method other than MLE. Another method I've read about but not really looked into is called kernel density estimation, but it doesn't seem like it would produce good results here either. What other methods for CPD learning are there? I'm investigating.
* Choose parametric CPDs anyway and learn them with a better scheme than MLE. MLE seems like a very naive learning method. A more judicious choice of CPDs could only help, but it's very difficult to come up with a likely CPD for the triangle-drawing method I've outlined below.
* Choose a drawing scheme other than the triangle-drawing method, one that suggests a more judicious choice of CPDs.
* Reduce CPD size by choosing much smaller images, perhaps even grayscale.
* Scrap the Bayesian net approach and choose a different machine learning technique. I'll have to read more about ML in general to decide the viability of another approach.

In fact, thinking about it, the triangle-drawing method has more parameters than just naively considering all the pixels in an image as independent parents to artiness.

Here's a StackOverflow question I asked on this topic: http://stackoverflow.com/questions/26917316/learning-nonparametric-discrete-cpds-in-a-bayesian-network

--------------
I've come up with an idea for generating images, thoughts below. The main point: use probabilistic graphical models and parameter learning to generate images, and learn the parameters incrementally using user votes as a score function for candidates.

Some links of interest:
* http://www.cs.ubc.ca/~murphyk/Bayes/bnintro.html#learn
* https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers

A possible model for generating images: Draw triangles sequentially. Each subsequent triangle is directly connected to the previous triangle by some structure that we wish to learn. More generally, the structure connecting any two sequential triangles may be the same or different, but it will probably be simpler to assume they are the same. The observable random variables of triangles include vertex coordinates and rgb values. One may introduce other random variables which influence the CPDs of these fundamental observables.

The sequence terminates in an observable (tentatively) called "artiness". Observed artiness values are obtained by using the candidate model CPDs and structure to generate an image.

This requires a graph structure for triangle observables and for the relationship between sequential triangles. Reading a bit more, it may be desirable to try to learn structure. Is it possible to simulataneously learn structure and parameters?

------------------------------------------------

Bah! I wrote a detailed description of an approach to this problem, but a network error ate it. Briefly the idea is this:
<ol>
<li>Create a DAG for image generation that's a sequence of triangles terminating in a variable called artiness. </li>
<li>Use a DAG with known CPDs (either from a round of learning or some initialization) to generate a sequence of triangles  (t1,..,tn) given a threshold artiness _a_ and a threshold probability _p_ that satisfy:</li>
  <ol>
  <li>P(A>a | Tn=tn) > p, in otherwords given _a_ look for all possible _tn_ that satisfy the relation and pick one.</li>
  <li>P(Tn=tn | Tn-1=tn-1) > p, again given _tn_ look for all possible _tn-1_ that satisfy the relation and pick one.</li>
  </ol>
<li>Users generate training data by scoring the artiness of a sequence of triangles.</li>
<li>Training data is used to learn CPDs and we return to step 2 to generate images and generate more training data. Rinse and repeat.</li>
</ol>

In other words, the objects we'll need are:
<ol>
<li>A DAG with associated CPDs and appropriate structure; call it an artist model or AM. AMs have the following methods:</li>
  <ol>
  <li>Given a training set, the AM learns the most likely CPDs.</li>
  <li>Given thresholds _a_ and _p_ described above, AM generates a sequence of triangles.</li>
  </ol>
<li>An image model (in the Django sense of models) with:</li>
  <ol>
  <li>a sequence of triangles.</li>
  <li>an artiness score.</li>
  </ol>
<li>A triangle model with:</li>
  <ol>
  <li>vertex coordinates</li>
  <li>rgb values</li>
  </ol>
<li>A training set object, which is really just a set of our image models.</li>
</ol>
