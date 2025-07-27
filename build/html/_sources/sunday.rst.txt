.. _this_sunday:

Paper Reading Sundays
=====================

This page serves as the repository where I document intriguing research articles primarily focused on the field of computers that capture my interest.

The intended schedule for updating this page is *every Sunday*, although there may be instances where I may not be able to maintain it consistently.

March 26, 2023
--------------

This week: `Cramming More Components onto integrated circuits - Gordon
Moore
(1975) <https://www.cs.utexas.edu/~fussell/courses/cs352h/papers/moore.pdf>`__

April 02, 2023
--------------

This week: `Parallelism through Digital Circuit Design - John
O’Donnell <https://drops.dagstuhl.de/opus/volltexte/2008/1372/pdf/07361.ODonnellJohn.Paper.1372.pdf>`__

April 09, 2023
--------------

This week: `Reflections on Trusting Trust - Ken Thompson <https://www.cs.cmu.edu/~rdriley/487/papers/Thompson_1984_ReflectionsonTrustingTrust.pdf>`__

June 25, 2023
-------------

This week: `The Hardware Lottery - Sara Hooker [2020] <https://hardwarelottery.github.io/>`__

**Key Points**:

* The Hardware Lottery is when an idea succeeds because it utilizes or aligns with existing technologies or ideas. Building on existing ideas and taking advantage of compatibility provides significant leverage, which bold new ideas in computer science often lack.

* It starts with examples of Charles Babbage's Analytical Engine, which promised a computer with a stored program concept and was constructed in 1871. However, true progress in achieving that goal only came a century later after World War II when the required electromagnetic technologies were invented.

* Similarly, Deep Learning was discussed in journals since the early decades of computers, but it only achieved significant breakthroughs in the past few decades.

* Machine Learning (ML) requires substantial computational resources, and the prevalent notion of "Bigger is Better" exacerbates this need. To develop new, large models, researchers require special-purpose hardware since CPUs alone are insufficient.

* Special-purpose hardware can only be built for purposes that have lasting relevance, which influences research to focus in that direction.

* Moreover, deep learning may or may not be the sole approach to achieve human-like intelligence. Exploring alternative methods will provide insights into this question, but only if those ideas succeed in the hardware lottery.

July 16, 2023
-------------

This week: `How to be an effective researcher - Michael Nielsen <https://michaelnielsen.org/blog/principles-of-effective-research/>`__

**Key Points**:

* Common sense principles are not necessarily commonly practised
* Motivation and desire can be changed
* Have fun while doing research, stay healthy, and spend time with your family.
* "Anyone could do that", but nobody does
* Proactivty not reactivity towards situations
* Three factors responsible in achieving self-discipline: clarity, social
  environment, honesty
* Improve your environment
* There are problem solver and problem creators. Problem solvers find solutions
  to existing problems and creators think of newer problems .
* For problem solvers, have multiple solutions (don't stick just one)
* Creator's needs: taste and standard for whats important (unimportant problems
  are different to uninteresting problems). 
* Dont chase public appreciation with your research but at the same time, keep
  in mind what the research landscape as a whole requires. These constitute
  important problems.

July 30, 2023
-------------

This week: `Producing wrong data without doing anything obviously wrong! - Mytkowicz et. al. <https://dl.acm.org/doi/10.1145/1508284.1508275>`__

* *Measurement bias* is the phenomenon where faulty collection or data or
  invalid reasoning towards a conclusion as a result of faulty data causes
  incorrect understanding of a process being investigated.
* Measurement bias is ubiquitous and more often than not unpredictable.
* Detection and avoidance tends to be the best strategy to deal with it.
* Causal analysis is a general technique for determining if we have reached an
  incorrect conclusion from our data. Three step procedure: Suppose X causes Y
  is a conclusion. But there is a chance Z could be causing Y. First, create an
  **Intervention** to X. Change the system and **Measure** X. Now, **Confirm**
  if Y changes when X changed, if it did, our conclusion is correct.
* Causal analysis is not a way to acquire flawless data, rather it is to assure
  ourselves that the conclusions we reach after are valid.
