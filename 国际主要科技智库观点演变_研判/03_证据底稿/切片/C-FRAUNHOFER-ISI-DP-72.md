# C-FRAUNHOFER-ISI-DP-72 原文切片

- 原文：`03_证据底稿\原文PDF\C-FRAUNHOFER-ISI-DP-72.pdf`
- PDF页数：27
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 3

Fraunhofer ISI Discussion Papers Innovation Systems and Policy Analysis No. 72
Fraunhofer ISI | I

Contents
Abstract .......................................................................................................................................... 1
1 Introduction.................................................................................................................... 1
2 Background and literature review ............................................................................ 3
2.1 The Fraunhofer-Gesellschaft .......................................................................................................... 3
2.2 The social returns to R&D ............................................................................................................... 3
2.3 The economic value of public research ....................................................................................... 4
3 Methodology and data ................................................................................................ 5
3.1 The micro-to-macro approach....................................................................................................... 5
3.2 Parameterization of the CGE model simulations ...................................................................... 7
3.2.1 The data sources and the model ............................................................................................................................................... 7
3.2.2 Identification strategy .................................................................................................................................................................... 7
3.2.3 Control variables ............................................................................................................................................................................... 8
4 Results .............................................................................................................................. 9
4.1 Parameterization ............................................................................................................................... 9
4.1.1 Baseline results .................................................................................................................................................................................. 9
4.1.2 Robustness checks ......................................................................................................................................................................... 10
5 Results from the macroeconomic model .............................................................. 13
5.1 Scenarios ............................................................................................................................................ 13
5.2 Simulation results ............................................................................................................................ 14
5.2.1 Aggregate effects ........................................................................................................................................................................... 14
5.2.2 Sectoral effects ................................................................................................................................................................................ 15
6 Discussion and conclusion ........................................................................................ 16
7 References .................................................................................................................... 19

### PDF页 6

Fraunhofer ISI Discussion Papers Innovation Systems and Policy Analysis No. 72
Fraunhofer ISI | 1

Abstract
Estimating the economic returns to public science investments has been a key topic in economics.
However, while in particular microeconomic approaches have been proposed, only a few studies
have tried estimating the macroeconomic effects of public science investments. In this paper, we
propose a micro-rooted macro-modelling framework, which combines the strength of an econo-
metric causal identification of key effects with the power of a Computable General Equilibrium (CGE)
framework, and provides additional economic structure of the estimates allowing us a fine-grained
sectoral differentiation of all effects. Applying our approach to the German Fraunhofer-Gesellschaft,
the world's largest publicly funded organization for applied research, we show that macroeconomic
returns are - irrespective of econometric specification - a high multitude of the original investment
costs. In specific, the activities by the Fraunhofer-Gesellschaft increase Germany´s GDP by 1.6% and
employment by 437,000 jobs. Our CGE analysis further shows that the effects concentrate i n the
chemicals, pharmaceuticals, motor vehicles and machinery sectors. The substantial size of our esti-
mated effects corroborate recent macroeconomic evidence on the social returns to innovation.
1 Introduction
Following the insights of the central importance of public science for economic development from
various literatures in economics and social sciences (Nelson 1959, Nelson and Winter 1982, Romer
1990, Dosi and Nelson 2010), expenditures for science organizations take significant shares in pub-
lic budgets in most developed countries. Yet, the significant state investments have also resulted in
calls to justify the spending by proving sufficiently high economic returns (Schubert 2009). The
increased interest in the returns of science has resulted i n a large number of studies gathering
econometric evidence particularly on the micro-level of the firm. For example, Robin and Schubert
(2013) and Comin et al. (2018) show that collaborating with public science or organizations in-
creases firm productivity. The central problem is that the necessary causal link between investment
in public science and ensuing economic returns are easier to establish on the micro -level of e.g.
individual firms collaborating with scientific organizations. However, aggregating up from micro to
macro-economic effects is fraught with difficulties and at best leads to rough estimations because
they neglect the interdependencies between the various markets (Robin and Schubert 2013, Comin
et al. 2018). Other authors document the positive effects on firms' innovativeness (Lööf and
Broström 2008, Maietta 2015).
Yet, despite the accumulating micro -level evidence of the value of science, precise and causally
identified macro-level estimates, i.e. estimates of how important public science o rganizations are
for the overall economy, are very difficult to obtain. A number of studies have used input- output
models (Bürgel et al. 1996; Glückler et al. 2015; Kowalski et al. 2012), which try taking stock of ac-
counting data on university expenditures and apply macroeconomic multipliers to them. A severe
limitation of these approaches is that the value of public science organizations is reduced to their
observable monetary flows while the value of knowledge as the, arguably, most relevant output of
public science is not at all considered (Glückler et al. 2015, Schubert and Kroll 2015). Inspired by
Goldstein and Renault (2004) and Carree et al. (2014), Schubert and Kroll (2016) have recently pro-
posed a regional-econometric approach, which circumvents measuring the value of knowledge by
relying on robust statistical associations to infer to causality. Applying the model to German NUTS-
III regions, they found that universities have considerably positive effects on GDP and, at least in

### PDF页 9

Fraunhofer ISI Discussion Papers Innovation Systems and Policy Analysis No. 72
Fraunhofer ISI | 4

2.3 The economic value of public research
Previous scientific analyses of the economic value of public research have largely focused on uni-
versities. Most analyses have used input-output or Keynesian multiplier approaches when measur-
ing demand-oriented, tangible effects illustrated by monetary expenditure flows such as student
consumption expenditure, university investment expenditure, etc. (for example, Bürgel et al. 1996;
Glückler et al. 2013; Kowalski et al. 2012). These studies document an overall positive effect, which
is usually low with GDP-multipliers hovering between 1.5 and 2. While such multipliers are well in
the range of the returns associated with other public investments into infrastructures, this approach
ignores effects that are usually associated with intangible knowledge output (Glückler et al. 2015).
However, providing intangible knowledge-associated outputs are not only an inherent task of re-
search organisations but, arguably, the most significant drivers of the economic effects of scientific
institutions (Florax 1992, Schubert and Kroll 2015). In particular, Pastor et al. (2018) and Sudmant
(2009) argue that the gap between investments into public research and investments into physical
infrastructure is that physical investments only have a static effect on the economy while public
research has also a dynamic effect.
Measuring dynamic effects is considerably more diff icult because of the inherent unobservability
of knowledge. Not surprisingly, most analyses have used econometric techniques to infer to the
effects by exploiting statistical associations. One strand of the literature has focused on firm level
data. Examples include Lööf & Broström (2008), Maietta (2015), Robin and Schubert (2013) and
Comin et al. (2018), who document robustly positive effects on public research, on firm innovation
and productivity. While these results are suggestive of the considerable dynamic effects channelled
through the knowledge links between firms and science, inferring to the overall macro -economic
impacts, though not impossible, is still ridden with conceptual difficulties. In particular, Robin and
Schubert (2013) and Comin et al. ( 2018), who also derive macro-economic productivity estimates
from their firm-level regressions, stress the importance of macro-economic substitution and read-
justment effects resulting in interdependencies between producer, consumer, credit and labour -
markets as well as equilibrium processes. Since such interdependencies remain unaccounted for in
micro-econometric models, they therefore caution against the overinterpretation of their macro -
economic estimates.
Only a few studies have so far addressed the shortcomings resulting from the reliance on firm-level
data, implying that macro-economic estimates of the importance of public science remain scarce.
Recently, a few studies have appeared that try to estimate the macro-economic effects, which rely
on macro-econometric approaches. The earliest attempts are probably due to Goldstein and Re-
nault (2004) and Goldstein and Drucker (2006) who use metropolitan-level economics with univer-
sity data for the US. They find amongst others that in particular smaller city -areas benefit by sug-
gesting that universities may anchor agglomeration economies. A similar approach is followed by
Schlump and Brenner (2010) for Germany. A limitation of these works is that they did not deliver
precise macro-economic estimates of the value of public research but remained at a more abstract
level. In an attempt to overcome this limitation, Schubert and Kroll (2013; 2016) extended the meth-
odology put forward by Goldstein and Drucker (2006) to determine the effects of regional higher
education, including knowledge-based or supply-oriented effects, using statistical methods from
panel data econometrics. Schubert and Kroll (2013) have, in particular, classified the effects on re-
gional GDP per capita as significant, with an annual effect of approximately €190 billion for Germany
as a whole, which corresponded to roughly 10% of total German GDP. Since then, a selected num-
ber of additional macro -econometric analyses have appeared also relying on econometric tech-
niques to estimate the macro -economic effects. Pastor et al. (2018) using growth -accounting ap-
proaches provide evidence that universities account for roughly 11% of GDP in the European Union,
which although using a different methodology is remarkably similar to the figures obtained by

## T1_国家研发与方向设定

- PDF页8：sciences in the world. In 2020 it commanded a budget of € 2.8 billion (Fraunhofer-Gesellschaft 2021). FhG is organized as a private registered association (“eingetragener Verein, e.V.”) and receives base funding amounting to roughly 30% of its total budget (90% from the federal government and 10% from the regional government where the respective institute is located). The Fraunhofer Society comprises 72 re- search institutes located all over Germany. The institutes focus on different topics mostly in the field of engineering and natural sciences, though a few institutes, such as Fraunhofer ISI and Fraunhofer IAO, exist which are m ore related to social sciences and economics. FhG's mission makes it the natural organization to study the magnitude of scientific knowledge transfer to private firms. In

- PDF页9：or example, Bürgel et al. 1996; Glückler et al. 2013; Kowalski et al. 2012). These studies document an overall positive effect, which is usually low with GDP-multipliers hovering between 1.5 and 2. While such multipliers are well in the range of the returns associated with other public investments into infrastructures, this approach ignores effects that are usually associated with intangible knowledge output (Glückler et al. 2015). However, providing intangible knowledge-associated outputs are not only an inherent task of re- search organisations but, arguably, the most significant drivers of the economic effects of scientific institutions (Florax 1992, Schubert and Kroll 2015). In particular, Pastor et al. (2018) and Sudmant (2009) argue that the gap between investments into public research and investment

- PDF页19：ng distribution of the budget covered by this shock. This allows us to gauge the macroeconomic impacts of FhG activities and their distribution across sec- tors of the German economy. 5.2.1 Aggregate effects The long-run effects of Scenarios 1 and 2 on Employment, Investment and Government Revenue are provided in Table 6. We consider each effect in turn. As expected, the total effects for the entire budget (Scenario 2) are much larger than the effects of the considered private sector funding (Sce- nario 1). In 2016 about 43.7 million people were in employment in Germany (Destatis, 2016b). Under Sce- nario 1, this number increases by 0.21% in our model, creating about 92 thousand additional jobs in the long run. In section 4.2. we analyse the sectoral composition of these jobs. Scenario 2 creates 1.0

- PDF页19：y 0.45% or €2.85 billion in response to private FhG funding covered. This corresponds to a 2.4% increase or €15.2 billion in Scenario 2. Thus, even the more robust investment effect under Scenario 1 outweighs total FhG funding. Lastly, we consider the impact of FhG activities on government revenue. Under Scenario 1, govern- ment revenue increases by 0.21%, which is about €2.7 billion. The entire budget (Scenario 2) is associated with an increase of 1.1% in government revenue. This corresponds to about €14 billion. These increases are mainly driven by additional taxes on labour (note how the proportionate in- crease in employment roughly corresponds to the proportionate increase in government revenue) but the government also increases its incom e from capital taxes. Thus, there appears to be a sig- n

- PDF页19：nario 2) is associated with an increase of 1.1% in government revenue. This corresponds to about €14 billion. These increases are mainly driven by additional taxes on labour (note how the proportionate in- crease in employment roughly corresponds to the proportionate increase in government revenue) but the government also increases its incom e from capital taxes. Thus, there appears to be a sig- nificant tax multiplier for FhG investment. Table 6: Estimated effects of FhG private funding and total budget on key economic variables Variable Scenario 1 Scenario 2 GDP 0.31% 1.6% Employment 0.21% 1.0% Investment 0.45% 2.4% Government Revenue 0.21% 1.1%

- PDF页22：atures. Our econometric estimates of the returns to spending on public research are interesti ng in their own right for at least two reasons. Firstly, they show that spending on public research pays off with returns in a magnitude that is difficult to recover from other types of public investment opportuni- ties. In that respect, our findings reinforce claims to the overall value of science investments provid- ing an economic justification for them. Secondly, while indeed some studies exist on the economic returns to public spending on basic research (universities in particular), to date there are only very few studies on the economic value of applied public science organizations (RTOs), Comin et al. (2018) being a notable exception. While one may be tempted to take for granted that findings for universiti

- PDF页22：se investments has been available. Indeed, while our findings are supportive of public investments into applied research, they also raise an important conceptual question: if it is indeed true that applied research tends to provide fewer spill overs, it is not a priori clear why governments instead of private actors should invest into it. More specifically, if in the sense of Nelson (1959) applied research is not or at least to a much lower degree subject to knowledge spill overs, the private actors may well themselves provide these types of applied R&D activities, in particular if the returns are as high as our results suggest. Our results are subtly at odds with this view, because we highlight both that Fraunhofer activities pos- sess a value that goes beyond what the market would provide on its o

- PDF页23：some parts of this gap, we provided more structure to our econometric findings by feeding them into a CGE-model of the German economy, which allows us better to capture the economic effects on different sectors of the economy. From this we learn two important lessons. First, the government revenue generated by the additional economic activities more than compensates for the initial spending in financing the Fraunhofer’s budget. Second, industries that interact more with Fraunhofer, and that are typi- cally considered ‘knowledge intensive’, benefit the most from the stimulus driven by Fraunhofer activities with firms. We also find that industries linked to the supply chains of these sectors benefit from second order effects through the composition of their supply chains delivering further stimuli to

## T2_市场与产业政策边界

- PDF页18：get. The second shock, Scenario 2, simulates the knock -on effect of an increase in GDP corresponding to the entire 2016 budget (€2,081 million). Scenario 2 is an extrapolation of Scenario 1 because it assumes that aggregate FhG effects are distributed by sector in line with the private sector funding.

- PDF页19：egate effects The long-run effects of Scenarios 1 and 2 on Employment, Investment and Government Revenue are provided in Table 6. We consider each effect in turn. As expected, the total effects for the entire budget (Scenario 2) are much larger than the effects of the considered private sector funding (Sce- nario 1). In 2016 about 43.7 million people were in employment in Germany (Destatis, 2016b). Under Sce- nario 1, this number increases by 0.21% in our model, creating about 92 thousand additional jobs in the long run. In section 4.2. we analyse the sectoral composition of these jobs. Scenario 2 creates 1.0% additional employment, which equals about 437 thousand jobs. Next, we consider investment effects. In 2016, there was €634 billion investment into German capital (Destatis, 2016b). Scenario 1 esti

- PDF页20：hofer ISI | 15 5.2.2 Sectoral effects In this section, we illustrate how impacts from Scenario 1 are distributed across the 28 sector ag- gregation of the German economy considered in this analysis.5 As a reminder to the reader, in this scenario we only consider the €410 million private sector funding portion of the total FhG budget mapped to specific sectors. Assuming that private sector collaboration are good proxies 6 for the industrial pattern of the demand effects, this allows us to estimate where in the economy FhG ef- fects are concentrated. Table 7 reports percentage changes from the baseline in sectoral investment, employment and value added. As can be seen, most sectors are positively affected by the increased demand driven by Fraunhofer activities. The only exception is a small fall in employ

## T4_国际合作与开放

- PDF页20：across the 28 sector ag- gregation of the German economy considered in this analysis.5 As a reminder to the reader, in this scenario we only consider the €410 million private sector funding portion of the total FhG budget mapped to specific sectors. Assuming that private sector collaboration are good proxies 6 for the industrial pattern of the demand effects, this allows us to estimate where in the economy FhG ef- fects are concentrated. Table 7 reports percentage changes from the baseline in sectoral investment, employment and value added. As can be seen, most sectors are positively affected by the increased demand driven by Fraunhofer activities. The only exception is a small fall in employment in service sectors such as health, R&D and private services. The overall increase in demand puts upward pr

- PDF页26：ent. Journal of Comparative Economics, 41(3), 669-683. Lööf, H., & Broström, A. (2008). Does knowledge diffusion between university and industry increase innovativeness?. The Journal of Technology Transfer, 33(1), 73-90. Maietta, O. W. (2015). Determinants of university–firm R&D collaboration and its impact on innovation: A perspective from a low-tech industry. Research Policy, 44(7), 1341-1359. Mućk, J. (2017). Elasticity of substitution between labor and capital: robust evidence from developed economies. Narodowy Bank Polski. Education & Publishing Department. Nelson, R. R. (1959). The simple economics of basic scientific research. Journal of political economy, 67(3), 297-306. Winter, S. G., & Nelson, R. R. (1982). An evolutionary theory of economic change. University of Illinois at Urbana-Champaign'

## T5_供应链与技术依赖

- PDF页23：nding in financing the Fraunhofer’s budget. Second, industries that interact more with Fraunhofer, and that are typi- cally considered ‘knowledge intensive’, benefit the most from the stimulus driven by Fraunhofer activities with firms. We also find that industries linked to the supply chains of these sectors benefit from second order effects through the composition of their supply chains delivering further stimuli to the wider economy. Acknowledgements The work underlying this project has been supported by funding from the Fraunhofer-Gesellschaft. We acknowledge the contribution of Graeme Roy, University of Glasgow and Anton Knoche, Uni- versity of Strathclyde, for their input at the early stage of this research, and Rainer Frietsch for his help with the data to parametrise the simulations.

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

未自动命中；需人工按目录复核。

## T10_预见与优先领域

- PDF页3：....................................................................................................................................................................... 10 5 Results from the macroeconomic model .............................................................. 13 5.1 Scenarios ............................................................................................................................................ 13 5.2 Simulation results ............................................................................................................................ 14 5.2.1 Aggregate effects ........................................................................................................................................................................... 14 5.2.2 Sectoral effects .

- PDF页4：ed effects of FhG private funding and total budget on key economic variables ......................................................................................................................... 14 Table 7 Investment, Value Added, and Employment % change from the baseline in Scenario 1 ...................................................................................................................................... 15

- PDF页11：mate the economic contribution that 1€ spending on the Fraunhofer budget generates for the economy. This is discussed in detail in the following section. We multiply this estimate by the total Fraunhofer budget for 2016. This figure is then used to calibrate the counter- factual scenario in the CGE model. The structure of the CGE model is based on Lecca et al. (2014) and Devarajan and Go (1998). It represents Germany as an open economy that trades goods and services domestically and with the rest of the world. Production is represented by modelling competitive, profit maximizing firms that use a combination of capital, labour and intermediate inputs, produced both domestically and im- ported to produce a single homogeneous output. This is represented using a nested constant elas- ticity of the sub

- PDF页18：fer. While we do not have a strong prior on the expected direction of the changes over time (if any), our results showed that the macroeco- nomic effects of Fraunhofer on GDP appeared to increase rather than decrease somewhat over time. 5 Results from the macroeconomic model 5.1 Scenarios As discussed, the macroeconomic simulations consider a series of counterfactual simulations re- lated to the German economy with and without Fraunhofer by matching the macroeconomic GDP impacts from the microeconomic analysis presented in section 4. To estimate the total size of ex- ogenous demand shocks related to the production-expansion associated with FhG, we assume that the additional FhG budget has a causal impact on the German GDP through increasing the demand for production sectors engaged with FhG. The r

- PDF页18：e ∆𝐺𝐺𝐺𝐺𝑃𝑃 is the absolute change in GDP, B is the budget for FhG activities, and 𝛾𝛾 is the effect of FhG budget on GDP and takes values in the range of €21.13 - €21.67 as shown in Table 2. From this, we derive two distinct exogenous demand shocks. The first shock, referred to as Scenario 1, simulates the knock -on effect of an increase in GDP corresponding to considering a subset of FhG budget (€410 million) that we can map to specific production sectors, using data provided by Frietsch (2020). This scenario forms the core of our analysis, as we know the underlying sectoral distribution of the corresponding budget. The second shock, Scenario 2, simulates the knock -on effect of an increase in GDP corresponding to the entire 2016 budget (€2,081 million). Scenario 2 is an extrapolation of Scenario 1

- PDF页18：considering a subset of FhG budget (€410 million) that we can map to specific production sectors, using data provided by Frietsch (2020). This scenario forms the core of our analysis, as we know the underlying sectoral distribution of the corresponding budget. The second shock, Scenario 2, simulates the knock -on effect of an increase in GDP corresponding to the entire 2016 budget (€2,081 million). Scenario 2 is an extrapolation of Scenario 1 because it assumes that aggregate FhG effects are distributed by sector in line with the private sector funding.

- PDF页19：Fraunhofer ISI Discussion Papers Innovation Systems and Policy Analysis No. 72 Fraunhofer ISI | 14 Plugging these numbers into equation 3 and dividing the results by the total 2016 GDP, we find that Scenario 1 is associated with a 0.31% GDP increase and Scenario 2 with a GDP increase of 1.6%. 5.2 Simulation results In this section, we provide aggregate long -run effects on key economic variables for Scenario 1 (private funding) and Scenario 2 (entire budget). In addition, we provide sectoral long- run effects for Scenario 1, as we know the underlying distribution of the budget covered by this shock. This allows us to gauge the macroeconomic impacts of FhG activities and their distribution across sec- tors of the Germa

- PDF页19：effects for Scenario 1, as we know the underlying distribution of the budget covered by this shock. This allows us to gauge the macroeconomic impacts of FhG activities and their distribution across sec- tors of the German economy. 5.2.1 Aggregate effects The long-run effects of Scenarios 1 and 2 on Employment, Investment and Government Revenue are provided in Table 6. We consider each effect in turn. As expected, the total effects for the entire budget (Scenario 2) are much larger than the effects of the considered private sector funding (Sce- nario 1). In 2016 about 43.7 million people were in employment in Germany (Destatis, 2016b). Under Sce- nario 1, this number increases by 0.21% in our model, creating about 92 thousand additional jobs in the long run. In section 4.2. we analyse the sectoral
