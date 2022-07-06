import typing as t

from toolcraft.texipy import Command, Glossary, Acronym, make_symbols_tex_file, Fa, Color


papertitle = Command(
    latex="Order Vs. Chaos: Multi-trunk classifier for side-channel attack")

paperkeywords = Command(
    latex="multi-trunk "
          "\\and low accuracy "
          "\\and data-augmentation "
          "\\and improve accuracy "
          "\\and order vs. chaos "
)

tracewithid = Command(latex="\\(t_{#1}^{(#2)}\\)", num_args=2, default_value='*')

labelwithlk = Command(latex="\\((#2)_{#1}\\)", num_args=2, default_value='')

correctlabel = Command(latex=f"$(${str(Fa.check_circle(Color.green))}$)$")

wronglabel = Command(latex=f"$(${str(Fa.times_circle(Color.red))}$)$")

# pk = Glossary(name="praveek", description="Praveen Kulkarni")
# pka = Acronym(short_name="PK", full_name="Praveen Kulkarni")
sca = Acronym(short_name="SCA", full_name="\\textit{side-channel analysis}")
ta = Acronym(short_name="TA", full_name="\\textit{template-attack}")
mtovc = Acronym(short_name="MTOvC", full_name="\\textit{multi-trunk order vs. chaos}")
gllabel = Glossary(
    name="$(label)$",
    description="A target intermediate value defined as $label \\in Z = f(P, K)$, "
                "where $P$ is some public variable e.g., a plaintext, and $K$ is the "
                "part of a secret key the attacker wants to retrieve. If the target "
                "intermediate value is 8 bit, then $label$ can take one of 256 "
                "(i.e., $2^8$) values. Notation $(label)$ is always surrounded by "
                "round brackets and can have actual value instead of variable "
                "$label$ e.g. $(000), (001), ..., (255)$."
)
glnumexamples = Glossary(
    name="$M$",
    description="The number of side-channel measurements (i.e., traces) "
                "used for profiling."
)
glnumclasses = Glossary(
    name="$C$",
    description=f"The number of discrete values a {gllabel.name} can take. "
                f"This depends on the leakage model and number of bits in the target "
                f"intermediate value."
)
glnumtrunks = Glossary(
    name="$Tr$",
    description=f"The number of trunks used in {mtovc.short_name} binary classifier. "
                f"It is exactly equal to number of classes {glnumclasses.name} used in "
                f"standard classifier."
)
glnummtexamples = Glossary(
    name="$M_*$",
    description=f"The number of multi-trunk examples extracted from profiling dataset "
                f"made up of {glnumexamples.name} side channel measurements "
                f"(i.e., traces). Note that each training example is made up of "
                f"{glnumtrunks.name} traces and there are huge possible combinations "
                f"with which we can make such tuples. But you can limit this number "
                f"to $M_*$ to be comparatively very larger than "
                f"{glnumexamples.name} let's say "
                f"$M_* \\approx M \\times 10$."
)
glnumattackexamples = Glossary(
    name="$A$",
    description="The number of side-channel measurements (i.e., traces) "
                "used for attack."
)
glnummtattackexamples = Glossary(
    name="$A_*$",
    description=f"The number of multi-trunk examples extracted from attack dataset "
                f"made up of {glnumattackexamples.name} side channel measurements "
                f"(i.e., traces). Note that each attack example is made up of "
                f"{glnumtrunks.name} traces and there are huge possible combinations "
                f"with which we can make such tuples. But you can limit this number "
                f"to $A_*$ to be comparatively very larger than "
                f"{glnumattackexamples.name} let's say "
                f"$A_* \\approx A \\times 10$."
)
glacc = Glossary(
    name="$Acc$",
    description="Accuracy of the classifier."
)
glbacc = Glossary(
    name="$Acc_{base}$",
    description="$Acc_{base}$ is the accuracy of the "
                "\\texttt{tensorflow.estimator.BaselineClassifier} "
                "provided in tensorflow software "
                "\\cite{abadiTensorFlowLargeScaleMachine2016}. Note that such "
                "classifier ignores input data and will learn to predict the average "
                "value of each label. In short it will predict the probability "
                "distribution of the classes as seen in the labels. These numbers "
                "are more desirable especially in case of class-imbalance."
)
gltgezero = Glossary(
    name="$T_{GE0}$",
    description="The number of side-channel measurements (i.e., traces) "
                "required to reach guessing entropy ($GE$) equal to zero."
)
gltraceith = Glossary(
    name="$t_{i}^{(label)}$",
    description="The $i^{th}$ out of $M$ side-channel measurement $t$ "
                "(i.e., trace) with corresponding target intermediate-value "
                f"{gllabel.name}."
)
gltracestar = Glossary(
    name="$t_{*}^{(label)}$",
    description="A randomly picked side-channel measurement $t$ (i.e., trace) "
                "from subset of $M$ traces which has target intermediate-value "
                f"{gllabel.name}. For ordered examples {gllabel.name} is same as "
                f"corresponding trunk while for chaos examples {gllabel.name} is not "
                f"equal to corresponding trunk."
)

gldstoytwobit = Glossary(
    name="\\texttt{2-bit toy dataset}",
    description="Two bit toy dataset simulated to leak hamming-weight leakage."
)

gldstoyeightbit = Glossary(
    name="\\texttt{8-bit toy dataset}",
    description="Eight bit toy dataset simulated to leak hamming-weight leakage."
)

gldssim = Glossary(
    name="\\texttt{simulated}",
    description="Simulated dataset."
)

gldssimnoisy = Glossary(
    name="\\texttt{simulated-noisy}",
    description="Simulated dataset with noise."
)

gldsascadvonefk = Glossary(
    name="\\texttt{ascad-v1-fk}",
    description="ASCAD v1 dataset for fixed key."
)

gldsascadvonevk = Glossary(
    name="\\texttt{ascad-v1-vk}",
    description="ASCAD v1 dataset for variable key."
)


make_symbols_tex_file()
