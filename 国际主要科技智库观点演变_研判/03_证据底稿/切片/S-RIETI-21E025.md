# S-RIETI-21E025 原文切片

- 原文：`03_证据底稿\原文PDF\S-RIETI-21E025.pdf`
- PDF页数：19
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 2

RIETI Discussion Paper Series 21-E-025
March 2021
Revised version August 2021

New indicator of science and technology inter-relationship by using text information of research
articles and patents in Japan1

Kazuyuki Motohashi (RIETI)
 Hitoshi Koshiba (NISTEP, AIST)
Kenta Ikeuchi (RIETI)

Abstract

In this study, the text information of academic papers (about 2.3 million) published by Japanese
authors and patents filed with the Japan Pa tent Office (about 12 million) since 1990) are used for
analyzing the inter -relationship between science and technology. Specifically, a distributed
representation vector using the title and abstract of each document is created, then neighboring
documents to each are extracted using cosine similarity. A time trend and sector specific linkage of
science and technology are identified by using the count of neighbor patents (papers) for each paper
(patent). It is found that the number of pa pers with similar contents of pa tents decreased over time
while the trend of patent counts with similar contents of paper is relatively stable. It is also found that
the scope of scientific discipline by papers is relatively stable, while the technology fields by patents
shows more dynamic patterns. This paper proposes a new methodology of measuring science and
technology interlinkage by using textual information as a complement to traditional indicators based
on non-patent literature citations of patents.

Keyword: Text analysis; patent information; research paper; science and technology linkage

JEL Classification：O31, O34

1 This study was conducted as part of the “Digitalization and Innovation Ecosystem: Holistic
Approach” project undertaken at the Research Institute of Economy, Trade and Industry (RIETI).
The authors would like to thank Professor Nagaoka and RIETI
discussion paper seminar participants for their helpful comments. An early version of this paper was
published as NISTEP Discussion Paper No. 175 (in Japanese). The authors also acknowledge
financial support from MEXT/JSPS KAKENHI (Grant Numbers: 18H03631, 18K12787).

### PDF页 4

2

abstracts from research papers and patents published by Japanese authors and inventors in the
years 1990–2018. We grouped the documents with high-content similarity and clarified the mutual
relationship between research papers and patents in the context of the advancement of science and
technology. In this paper, Chapter 2 describes our method of analysis and Chapter 3 presents an
outline of our obtained data, as well as the results from a cluster analysis. In Chapter 4, we use
citation information from research papers and patents to perform an evaluation of a similarity
index via text mining—the method we use in this present paper. In Chapter 5, we present a relation
index of science and technology and show the trends in the relationship between the two in Japan.
Finally, we present our conclusion and describe future issues to be examined.

2. Data sets and text mining techniques
2.1. Data sets
In this paper, to comprehensively observe the interlinking relationship between Japanese science and
technology, we used the following data sets:
· Research paper information: Papers included in Science Citation Index expanded from
Clarivate’s Web of Science, published between 1990 and 2017, and containing at least one
Japan-based author.
· Patent information: Patents filed with the Japan Patent Office and included in the
PATSTAT2020 Spring Version (those for which English-translated title and abstract
information are available).
Regarding the number of documents, we used 2,342,987 research papers and 12,037,068 patents,
for a total of14,380,055 documents.
Figure 1 shows the changes in the number of documents by publication year (for patents, the
application year). The number of patents shows a declining trend since 2000, while the number of
research papers remains stable, with ~100,000 publications per year.

### PDF页 5

3

Figure1 : Numbers of papers and patents by application/publication year

2.2. Text mining method and clustering results
To create document embedding vectors that represent the content of each document, we used
two steps. We first created embeddings for each word and then aggregated them by document.
First, we extracted only the nouns that appear in a total of ~14.3 million titles and abstracts and
used FastText (Joulin, 2016; Bojanowki, 2017) to create embedding vectors for words other than
common words and rare words. Next, we took the average of these word vectors to obtain a
document embedding vector for each document. Regarding embedding results for the words, we
conducted cluster analysis using the K-means method and confirmed, by visual checking, that
semantically similar words belonged in the same cluster (for details, see Motohashi, Koshiba, and
Ikeuchi, 2021).
The embedding results of the words were aggregated for each document. We clustered these
using the K-means method (classification with 16 clusters) and compressed the results into two
dimensions using UMAP (McInnes et al., 2018). The result is shown in Figure 2.

## T1_国家研发与方向设定

未自动命中；需人工按目录复核。

## T2_市场与产业政策边界

未自动命中；需人工按目录复核。

## T4_国际合作与开放

未自动命中；需人工按目录复核。

## T5_供应链与技术依赖

未自动命中；需人工按目录复核。

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

未自动命中；需人工按目录复核。

## T10_预见与优先领域

未自动命中；需人工按目录复核。
