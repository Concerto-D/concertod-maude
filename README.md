# A Maude Formalization of the Decentralized Reconfiguration Language Concerto-D

## Overview

Running and maintaining large-scale distributed software is now a commonplace activity, but managing
the inherent complexity of this task requires dedicated tools, models, and languages. The complexity
is particularly apparent when distributed software needs to be reconfigured during execution, either to
satisfy changing requirements or to carry out maintenance operations.

Concerto-D is a reconfiguration language that extends the Concerto language[^2]. It improves on two different parameters compared with related work: the decentralized coordination of numerous local reconfiguration plans which avoid a single point of failure when considering unstable networks such as edge computing, or cyber-physical systems (CPS) for instance; and a mechanized formal semantics of the language with Maude, a language and system that supports both equational and rewriting logic specification and programming.

*An Overview of the Decentralized Reconfiguration Language Concerto-D through its Maude Formalization*[^1] is a companion paper to this software.

## Authors

- Hélène Coullon, IMT Atlantique, France
- Farid Arfi, IMT Atlantique, France
- Frédéric Loulergue, Université d'Orléans, France
- Jolan Philippe, IMT Atlantique, France
- Simon Robillard, Université de Montpellier, France

## Requirements

- [The Maude System](https://maude.cs.illinois.edu/wiki/The_Maude_System) version 3.4

## Usage

Loading the file `0_Main.maude` launches the load of all the files of the formalization including the example described in the paper. Two searches for final configurations from an initial one are launched: the first one succeeds and the second one fails because the target configuration describes an incorrect state.


[^1]: Farid Arfi, Hélène Coullon, Frédéric Loulergue, Jolan Philippe, and Simon Robillard. An Overview of the Decentralized Reconfiguration Language Concerto-D through its Maude Formalization. In 17th Interaction and Concurrency Experience (ICE), Electronic Proceedings in Theoretical Computer Science, 2024
[^2]: Maverick Chardet, Hélène Coullon, Simon Robillard. [Toward safe and efficient reconfiguration with Concerto](https://doi.org/10.1016/j.scico.2020.102582). Sci. Comput. Program. 203, 2021
