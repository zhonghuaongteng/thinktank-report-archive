# Accelerating Materials Science with AI and Robotics

- 报告ID：C-FAS-2024-ACCELERATING-MATERIALS-SCIENCE-WITH-AI-AND-ROBOTICS
- 机构：Federation of American Scientists
- 科技创新复用角色：将材料数据、科学基础模型和自驱动实验室组织为公共研发能力的2024技术路线节点
- 主轴：材料发现；科学基础模型；科研数据；机器人实验室；公共研发设施；成果转化

## 科学技术创新定向摘录

Innovations in materials science enable innumerable downstream innovations: steel enabled skyscrapers, and novel configurations of silicon enabled microelectronics. Yet progress in materials science has slowed in recent years. Fundamentally, this is because there is a vast universe of potential materials, and the only way to discover which among them are most useful is to experiment. Today, those experiments are largely conducted by hand. Innovations in artificial intelligence and robotics will allow us to accelerate the search process using foundation AI models for science research and

Each of these questions implicates materials science in fundamental ways. The limits of our technological capabilities are defined by the limits of what we can build, and what we can build is defined by what materials we have at our disposal. The early eras of human history are named for materials: the Stone Age, the Bronze Age, the Iron Age. Even today, the cradle of American innovation is

Materials science has been a driver of economic growth and innovation for decades. Improvements to silicon purification and processing—painstakingly worked on in labs for decades—fundamentally enabled silicon-based semiconductors, a

(BEA) at $3.7 trillion in the U.S. alone, in turn, rests on semiconductors. Plastics, another profound materials science innovation, are

Yet materials science and engineering—the disciplines of discovering and learning to use new materials—have slowed down in recent decades. The low-hanging fruit has been plucked, and the easy discoveries are old news. We’re approaching the limits of what our materials can do because we are also approaching the limits of what the traditional practice of materials

Today, materials science proceeds at much the same pace as it did half a century ago: manually, with small academic labs and graduate students formulating potential new combinations of elements, synthesizing those combinations, and studying their characteristics. Because there are more ways to configure matter than there are atoms in the universe, manually searching through the space of possible materials is an impossible task.

Achieving this goal will require a coordinated effort, significant investment, and expertise at the frontiers of science and engineering. Because much of materials science is basic R&D—too far from commercialization to attract private investment—there is a unique opportunity for the federal government to lead the way. As with much scientific R&D, the economic benefits of new materials science discoveries may take time to emerge. One literature review

that it can take roughly 20 years for basic research to translate to economic growth. Research indicates that the returns—once they materialize—are significant. A study from the Federal Reserve Bank of Dallas

The best-positioned department within the federal government to coordinate this effort is the DOE, which has many of the key ingredients in place: a demonstrated track record of building and maintaining the supercomputing facilities required to make physics-based AI models, unparalleled scientific datasets with which to train those models collected over decades of work by national labs and other DOE facilities, and a skilled scientific and engineering workforce capable of bringing challenging projects to fruition.

Developing foundation AI models for materials science discovery

, either independently or in collaboration with the private sector (estimated cost: $10-100 million, depending on the nature of the collaboration);

, building a supply chain for robotics and other equipment, and validating the scientific merit of SDLs (estimated cost: $20-40 million);

The total cost of the proposal, then, is estimated at between $130-240 million. The potential return on this investment, though, is far higher. Moderate improvements to battery materials could drive tens or hundreds of billions of dollars in value.

Before a large materials science foundation model can be trained, vast datasets must be assembled.

DOE, through its large network of scientific facilities including particle colliders, observatories, supercomputers, and other experimental sites, collects enormous quantities of data

, recognizing the problems with DOE data infrastructure, suggests developing federated learning capabilities–an active area of research in the broader machine learning community–which would allow for data to be used for training

This work will require deep collaboration between data scientists, machine learning scientists and engineers, and domain-specific scientists. It is, by far, the least glamorous part of the process–yet it is the necessary groundwork for all progress to follow.

Foundation models for materials science can take many different forms, incorporating various aspects of physics, chemistry, and even—for the emerging field of

models can help materials science in two ways: inverse design and property prediction.

DOE has already proposed creating AI foundation models for materials science as part of its

Frontiers in Artificial Intelligence for Science, Security and Technology (FASST)

initiative. While this initiative contains numerous other AI-related science and technology objectives, supporting it would enable the creation of new foundation models, which can in turn be used to support the broader materials science work.

DOE’s long history of stewarding America’s national labs makes it the best-suited home for this proposal. DOE labs and other DOE sub-agencies have decades of data from particle accelerators, nuclear fusion reactors, and other specialized equipment rarely seen in other facilities. These labs have performed hundreds of thousands of experiments in physics and chemistry over their lifetimes, and over time, DOE has created standardized data collection practices. AI models are defined by the data that they are trained with, and DOE has some of the most comprehensive physics and chemistry datasets in the country—if not the world.

The foundation models created by DOE should be made available to scientists. The extent of that availability should be determined by the sensitivity of the data used to train the model and other potential risks associated with broad availability. If, for example, a model was created using purely internal or otherwise sensitive DOE datasets, it might have to be made available only to select audiences with usage monitored; otherwise, there is a risk of exfiltrating sensitive training data. If there are no such data security concerns, DOE could choose to fully open source the models, meaning their weights and code would be available to the general public. Regardless of how the models themselves are distributed, the fruits of all research enabled by both DOE foundation models and self-driving labs should be made available to the academic community and broader public.

Self-driving labs are largely automated facilities that allow robotic equipment to autonomously conduct scientific experiments with human supervision. They are well-suited to relatively simple, routine experiments—the exact kind involved in much of materials science. Recent advancements in robotics have been driven by a combination of cheaper hardware and enhanced AI models. While fully autonomous humanoid robots capable of automating arbitrary manual labor are likely years away, it is now possible to configure facilities to automate a broad range of scripted tasks.

Many experiments in materials science involve making iterative tweaks to variables within the same broad experimental design. For example, a grad student might tweak the ratios of the elements that constitute the material, or change the temperature at which the elements are combined. These are highly automatable tasks. Furthermore, by allowing multiple experiments to be conducted in parallel, self-driving labs allow scientists to rapidly accelerate the pace at which they conduct their work.

Creating a successful large-scale self-driving lab will require collaboration with private sector partners, particularly robot manufacturers and the creators of AI models for robotics. Fortunately, the United States has many such firms. Therefore,

The United States already has several small-scale self-driving labs, primarily led by investments at DOE National Labs. The small size of these projects, however, makes it difficult to achieve the economies of scale that are necessary for self-driving labs to become an enduring part of America’s scientific ecosystem.

AI creates additional opportunities to expand automated materials science. Frontier language and multi-modal models, such as OpenAI’s

, have already been used to ideate scientific experiments, including

Modern frontier models have substantial knowledge in all fields of science, and can hold all of the academic literature relevant to a specific niche of materials science within their active attention. This combination means that they have—when paired with a trained human—the scientific intuition to iteratively tweak an experimental design. They can also write the code necessary to direct the robots in the self-driving lab. Finally, they can write summaries of the experimental results—including the failures. This is crucial, because, given the constraints on their time, scientists today often only report their successes in published writing. Yet failures are just as important to document publicly to avoid other scientists duplicating their efforts.

Taken together, materials science faces a grand challenge, yet an even grander opportunity. Room-temperature, ambient-pressure superconductors—permitted by the laws of physics but as-yet undiscovered—could transform consumer electronics, clean energy, transportation, and even space travel. New forms of magnets could enable a wide range of cutting-edge technologies, such as nuclear fusion reactors. High-performance ceramics could improve reusable rockets and hypersonic aircraft. The opportunities are limitless.

With a coordinated effort led by DOE, the federal government can demonstrate to Americans that scientific innovation and technological progress can still deliver profound improvements to daily life. It can pave the way for a new approach to science firmly rooted in modern technology, creating an example for other areas of science to follow. Perhaps most importantly, it can make Americans

AI is a radically transformative technology. Contemplating that transformation in the abstract almost inevitably leads to anxiety and fear. There are legislative proposals, white papers, speeches, blog posts, and tweets about using AI to positive ends. Yet merely

about positive uses of AI is insufficient: the technology is ready, and the opportunities are there. Now is the time to act.

— our effort to bring forward bold policy ideas, grounded in science and evidence, that can tackle the country’s biggest challenges and bring us closer to the prosperous, equitable and safe future that we all hope for whoever takes office in 2025 and beyond.

Compared to “cloud labs” for biology and chemistry, the risks associated with self-driving labs for materials science are low. In a cloud lab equipped with nucleic acid synthesis machines, for example, genetic sequences need to be screened carefully to ensure that they are not dangerous pathogens—a nontrivial task. There are not analogous risks for most materials science applications.

DOE can and should be creative and resourceful in finding additional resources beyond public funding for this project. Collaborations on both foundation AI models and scaling self-driving labs between DOE and private sector AI firms can be uniquely facilitated by DOE’s new

(FESI), a private foundation created by DOE to support scientific fellowships, public-private partnerships, and other key mission-related initiatives.

, a materials science model that identified thousands of new potential materials (though they need to be experimentally validated). Microsoft’s

model pushed in a similar direction. Both models were developed in collaboration with DOE National Labs (Lawrence Berkeley in the case of DeepMind, and Pacific Northwest in the case of Microsoft).
