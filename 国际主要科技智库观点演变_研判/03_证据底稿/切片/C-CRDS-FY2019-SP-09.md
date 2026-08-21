# C-CRDS-FY2019-SP-09 原文切片

- 原文：`03_证据底稿\原文PDF\C-CRDS-FY2019-SP-09.pdf`
- PDF页数：54
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 6

STRATEGIC PROPOSAL
The Next Generation Blockchain Technology

CRDS-FY2019-SP-09 Center for Research and Development Strategy, Japan Science and Technology Agency
iv
Executive Summary

Blockchain technology serves as a fundamental technology for sharing data and
exchanging value among people and society. In this proposal we identify issues for basic
research and application development, and propose strategies for technology development
toward the secure and trustworthy social infrastructure.
Blockchain is a form of distributed ledger in which blocks of data are “chained”
consecutively in a network. In 2008 a paper written by Satoshi Nakamoto gave rise to Bitcoin,
the first implementation of Blockchain. The following year he released an open source of
Bitcoin, which has been in operation for more than 10 years to date. Technologies used in
Bitcoin, such as cryptography, P2P networks and distributed systems, the mechanism of
incentives for distributed consensus building, and continuous operation are not particularly
new. These technologies which enabled Bitcoin are collectively referred t o “Blockchain
technology”, especially the first generation blockchain technology in this proposal.
The success of Bitcoin has revealed that cryptographic proof of trust allows direct
transactions between parties on the Internet without trusted third partie s. Blockchain, the
core technology of Bitcoin, has attractive functions and features such as distributed ledger,
immutability, traceability, distributed consensus mechanism, and transaction functions. For
this reason, expectations as general -purpose techno logy applicable to other than
crypto-assets have increased, and emerging blockchain technology have been researched and
implemented. Moreover, Blockchain itself is evolving by introducing new technology. One
example is smart contract, which is a program in corporated in transaction data to enable
exchange various values automatically. Another is a second layer technology which
accelerates transaction speed much faster than Bitcoin which intentionally processes only
about several transactions per second due t o its design philosophy. These extensions to the
first generation lead the Blockchain to the second generation. We are now still at this stage.
Accordingly, the various demonstration experiments and platforms conducted around the
world are mainly based on this stage of technology.
We believe the basic research and application development to establish secure and
trustworthy infrastructures for data -sharing and value -exchange among people and society.
To this end, there lies a wide variety of issues to be sol ved from basic research to application
development such as securing scalability with the expansion of use of data, handling personal
data that should not be disclosed, supporting cryptography in the quantum computer era and
so on, as well as re -designing business practices and systems corresponding to completely
new technology.
In this proposal we position the blockchain technology as "a fundamental technology for
safely and reliably realizing the sharing of important personal and social data and the
exchange of value." While the Internet is the basis for information exchange, th e Blockchain
will be the basis for value exchange. However, current blockchain technology is as immature
as the dawning of Internet in senses both fundamental and application technology. The

### PDF页 9

戦略プロポーザル
次世代ブロックチェーン技術～個人や社会のデータ共有・価値交換を安全で高信頼に実現する～

CRDS-FY2019-SP-09 Center for Research and Development Strategy, Japan Science and Technology Agency

目 次

エグゼクティブサマリー
Executive Summary
１. 研究開発の内容 ·································································· 1
１.１ ブロックチェーンとは ······················································· 1
１.２ 提案する研究開発の概要 ····················································· 2
１.３ 推進方法 ··································································· 4
２. 研究開発を実施する意義 ·························································· 6
２.１ 現状認識および問題点 ······················································· 6
２.２ 社会・経済的効果 ·························································· 10
２.３ 科学技術上の効果 ·························································· 17
３. 具体的な研究開発課題 ··························································· 19
３.１ 問題点と研究開発課題の俯瞰 ················································ 19
３.２ ブロックチェーンを構成する技術 ············································ 20
３.３ プラットフォームおよびアプリケーション ···································· 22
４. 研究開発の推進方法および時間軸 ················································· 25
４.１ 研究開発による基礎基盤の確立 ·············································· 25
４.２ わが国の国家的社会基盤への適用 ············································ 26
４.３ ブロックチェーンの活用と影響を議論する場の設定 ···························· 28
付録１．検討の経緯 ································································· 30
付録１.１ 有識者インタビュー ···················································· 30
付録１.２ 科学技術未来戦略ワークショップ ········································ 31
付録１.３ 俯瞰活動 ······························································ 33
付録２ 国内外の状況 ································································ 34
付録２.１ 論文・特許で見た国内外の状況 ·········································· 34
付録２.２ わが国における活動状況 ················································ 37
付録３ 専門用語 ···································································· 39
付録４ 参考文献 ···································································· 41

## T1_国家研发与方向设定

- PDF页7：earch as well as the research community is dispersed in silos. （２） Apply blockchain to the national social infrastructure By establishing Japan's national social infrastructure using Blockchain, it is possible to realize a safe, transparent, and efficient next-generation digital government ahead of the rest of the world as part of the realization of "Society 5.0", the future social image that Japan aims for. To do so, first, we need the grand design of the next generation digital government, especially data strategy is critical. Then the data exchange infrastructure based on blockchain is to be built and applied to the national social infrastructure. Applications that link digital government services and private services will be developed in some specific test areas. However, seeing the case of Esto

- PDF页7：. To do so, first, we need the grand design of the next generation digital government, especially data strategy is critical. Then the data exchange infrastructure based on blockchain is to be built and applied to the national social infrastructure. Applications that link digital government services and private services will be developed in some specific test areas. However, seeing the case of Estonia, rebuilding the social infrastructure takes a long time. Strong will of the government is crucial for its realizati on. Discussions on digital government have already begun in Japan regardless of emerging technology such as Blockchain. It is important to take technical discussion into consideration. In addition, it is necessary to simultaneously build a body of knowledg e for utilizing the national soci

- PDF页17：ている。EU Blockchain Initiative は EU 全体の基盤構 築を検討しつつ、複数のプロジェクトを走らせている。2018 年には、ブロックチェーンによるイ ノベーションの加速と EU 内のブロックチェーンエコシステムの開発を目的とした EU Blockchain Observatory and Forum を設立した。100 名規模の有識者によるフォーラム活動を 精力的に実施し、 ”Blockchain Innovation in Europe”、”Blockchain and the GDPR ”、” Blockchain for Government and Public Services ”等の質の高いレポートを発行している。 Digital Single Market も 2017 年の中間評価でブロックチェーンに関連づけられた。他にも、 ” Horizon Prize on Blockchains for Social Good ”や暗号資産に関するプロジェクトもイニシア ティブの下で開発が進められている。 Wien 工科大学の Matteo Maffei 教授が率いる研究グループが、Ethertrust プロジェクトによ り、Ethereum のスマートコントラクトのセキュリティーを向上させる研究成果を 2017 年 11 月 末に発表した。スウェーデンのチャルマース工科大学（Chalmers University of Technology）で は、公平なモビリティサービスに向けたMaaS（Mobility as a Service）におけるブロックチェー ン技術の役割について研究している。 フィンランドのAalto 大学は、Pekka Nikander 教授をリー 7 PoA では、トランザクションとブロックは、バリデーターと呼ばれる承認済みのアカウントによ

- PDF页39：～ CRDS-FY2019-SP-09 国立研究開発法人科学技術振興機構 研究開発戦略センター 29 ４ ． 研 究 開 発 の 内 容 の 推 進 方 法 お よ び 時 間 軸 ションの加速とEU内のブロックチェーンエコシステムの開発を目的に設立されたEU Blockchain Observatory and Forum の活動である。100 名規模の有識者によるフォーラム活動を精力的に実 施し、”Blockchain Innovation in Europe” 、”Blockchain and the GDPR” 、”Blockchain for Government and Public Services”等の質の高いレポートを発行している16。 具体的な会議の母体は基本的に以下に示すような既存の組織において定常的に実施する形でよ い。  電子政府に関する議論：内閣府 IT 戦略室など  金融分野における議論：金融庁 Fintech 室、日本銀行金融研究所など  イノベーションに関する議論：経済産業省 RIETI など 情報交換・議論の機会を設けたり、社会からの意見を聞く機会として、合同でセミナーやワー クショップを開催することも重要である。また、情報システムにおける議論に関しては、 EU Blockchain Observatory and Forum やコンサルファーム （Gartner や Deloitte トーマツ、 など） と意見交換する必要がある。 また、情報システムにおける議論に関しては、EU Blockchain Observatory and Forum やコ ンサルファーム（Gartner や Deloitte トーマツ、など）と意見交換する必要がある。 16 EU Blockchain Observatory and Forum An Initiative

- PDF页39：ockchain Observatory and Forum やコ ンサルファーム（Gartner や Deloitte トーマツ、など）と意見交換する必要がある。 16 EU Blockchain Observatory and Forum An Initiative of the European Commision, https://www.eublockchainforum.eu/. 発行されたレポート :Blockchain innovation in Europe,Blockchain and the GDPR,Blockchain for Government and Public Services,Scalability, interoperability and sustainability of blockchains(2018),Blockchain and Digital Identity (2019)

- PDF页51：] MIT Technology Review Japan (編), “Blockchain 2「非中央集権化」 の先にあるもの”, MIT テクノロジーレビュー Special Issue Vol. 10 (角川アスキー総合研究所, 2018). [15] EU Blockchain Observatory and Forum, Thematic report s on “Blockchain innovation in Europe” (2018), “Blockchain and the GDPR” (2018), “Blockchain for Government and Public Services” (2018), “Scalability, interoperability and sustainability of blockchains” (2019), “Blockchain and Digital Identity” (2019), “Leg al and regulatory

## T2_市场与产业政策边界

未自动命中；需人工按目录复核。

## T4_国际合作与开放

- PDF页51：和恵, 佐藤雅史, 林達也, 古川諒, 宮澤慎一,『ブロッ クチェーン技術の未解決問題』(日経 BP, 2018). [6] 赤羽喜治, 愛敬真生,『ブロックチェーン 仕組みと理論』増補改訂版 (リックテレコム, 2019). [7] 山際貴子, “スマートコントラクトとは？ブロックチェーン活用の仕組みとKDDI の実証実 験を紹介”. ボクシルマガジン・ビヨンド (2018.01.10) https://boxil.jp/beyond/a3594/ (accessed 2020-3-4) [8] Karen D . Frazer, NSFNET: A partnership for high -speed networking : final report, 1987-1995 (Merit Network, 1996). [9] 砂原秀樹, 村井純, “WIDE プロジェクトの 25 年 日本とインターネットのこれまでとこれ から”, 情報管理 Vol. 56 No. 9 (2013) pp.571-581. [10] David Chaum, “Blind Signatures for Untraceable Payments”, Advances in Cryptology: Proceedings of Crypto 82 (Santa Barbara, California, August 23-25, 1982) pp 199-203. [11] e-Governance Academy, “e-Estonia: e-Governance in Practice” https://ega.ee/publication/e-estonia-e-governance-in-practice-2/ (accessed 2020-3-4) ; 三菱 UFJ リサーチ&コンサルティング (訳

## T5_供应链与技术依赖

- PDF页21：グ、価値流通、権利証明などにおいて 67 兆円にのぼるといわれている8。ま た、世界経済フォーラムのレポートでは、ブロックチェーンによる障壁の撤廃により、今後 10 年間に 1 兆ドル規模以上の貿易が新たに生まれる可能性があると指摘されている9。 8 経済産業省、平成 27 年度 我が国経済社会の情報化・サービス化に係る基盤整備（ブロックチェーン技術を利用したサービスに関 する国内外動向調査）報告書、2016 年 4 月 28 日 9 World Economic Forum, “Trade Tech – A New Age for Trade and Supply Chain Finance”, Sep. 2018

- PDF页52：戦略プロポーザル 次世代ブロックチェーン技術～個人や社会のデータ共有・価値交換を安全で高信頼に実現する～ CRDS-FY2019-SP-09 国立研究開発法人科学技術振興機構 研究開発戦略センター 42 framework of blockchains and smart contracts” (2019), “Blockchain in trade finance and supply chain” (2019), and “Blockchain and the future of digital assets” (2020). https://www.eublockchainforum.eu/reports (accessed 2020-3-4) [16] Rajesh Kandaswamy and David Furlonger, Gartner Research on “Pay Attention to These 4 Types of Blockchain Business Initiatives” (Gartner, 2018). [17] 経済産業省, 平成 27 年度 我が国経済社会の情報化・サービス化に係る基盤整備（ブロッ クチェーン技術を利用したサービスに関する国内外動向調査）報告書 (2016). [18] World Economic Forum, White Paper “Trade Tech – A New Age for Trade and Supply Chain Finance” (2018). https://www.weforum.org/whitepapers/trade-tec

- PDF页52：longer, Gartner Research on “Pay Attention to These 4 Types of Blockchain Business Initiatives” (Gartner, 2018). [17] 経済産業省, 平成 27 年度 我が国経済社会の情報化・サービス化に係る基盤整備（ブロッ クチェーン技術を利用したサービスに関する国内外動向調査）報告書 (2016). [18] World Economic Forum, White Paper “Trade Tech – A New Age for Trade and Supply Chain Finance” (2018). https://www.weforum.org/whitepapers/trade-tech-a-new-age-for-trade-and-supply- chain-finance (accessed 2020-3-4) [19] Bitcoin Exchange Guide News Team, “Spanish Ministry of Agriculture, Fisheries and Food Develops Blockchain App with ChainWood For Forestry Transparency ”, (September 24, 2018). https://bitcoinexchangeguide.com/spanish-ministry-of-agriculture-fisheries-and-food-d evelops-blockchain-app-with-chainwood-for-forestry-transparency/ (accessed 2020-3-4) [20] 川崎貴夫, “森づくり・木づかいの「見える化」促進に向けた I

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

- PDF页6：ry Blockchain technology serves as a fundamental technology for sharing data and exchanging value among people and society. In this proposal we identify issues for basic research and application development, and propose strategies for technology development toward the secure and trustworthy social infrastructure. Blockchain is a form of distributed ledger in which blocks of data are “chained” consecutively in a network. In 2008 a paper written by Satoshi Nakamoto gave rise to Bitcoin, the first implementation of Blockchain. The following year he released an open source of Bitcoin, which has been in operation for more than 10 years to date. Technologies used in Bitcoin, such as cryptography, P2P networks and distributed systems, the mechanism of incentives for distributed consensus building, and

- PDF页6：continuous operation are not particularly new. These technologies which enabled Bitcoin are collectively referred t o “Blockchain technology”, especially the first generation blockchain technology in this proposal. The success of Bitcoin has revealed that cryptographic proof of trust allows direct transactions between parties on the Internet without trusted third partie s. Blockchain, the core technology of Bitcoin, has attractive functions and features such as distributed ledger, immutability, traceability, distributed consensus mechanism, and transaction functions. For this reason, expectations as general -purpose techno logy applicable to other than crypto-assets have increased, and emerging blockchain technology have been researched and implemented. Moreover, Blockchain itself is evolving

- PDF页6：n to the second generation. We are now still at this stage. Accordingly, the various demonstration experiments and platforms conducted around the world are mainly based on this stage of technology. We believe the basic research and application development to establish secure and trustworthy infrastructures for data -sharing and value -exchange among people and society. To this end, there lies a wide variety of issues to be sol ved from basic research to application development such as securing scalability with the expansion of use of data, handling personal data that should not be disclosed, supporting cryptography in the quantum computer era and so on, as well as re -designing business practices and systems corresponding to completely new technology. In this proposal we position the blockchain

- PDF页7：will be developed in some specific test areas. However, seeing the case of Estonia, rebuilding the social infrastructure takes a long time. Strong will of the government is crucial for its realizati on. Discussions on digital government have already begun in Japan regardless of emerging technology such as Blockchain. It is important to take technical discussion into consideration. In addition, it is necessary to simultaneously build a body of knowledg e for utilizing the national social infrastructure and strategically develop human resources. Figure Blockchain Technology Stack

- PDF页8：nter for Research and Development Strategy, Japan Science and Technology Agency vi （３） Initiate forum activity for continuous discussions Given the potential innovations of blockchain technology, there is a need for discussions similar to that for t he human and social impact of artificial intelligence. Regular workshops and seminars to publish high -quality reports and recommendations, with the opportunity to discuss the essential insights of blockchain technology (e.g., realizing value and avoiding risks) are crucial. The Internet has transformed society and the way people live accordingly. By connecting computers and devices around the world digitally, it has become the "information exchange platform" that allows anyone to easily send, receive, search and use information. Blockchain, on the other hand, will p

- PDF页8：has become the "information exchange platform" that allows anyone to easily send, receive, search and use information. Blockchain, on the other hand, will provide the basis for ensuring the authenticity of data and making it easy to share and exchange values. This could be the "trustworthy platform" that anyone can trust the information on the blockchain based infrastructure. However, in order to reach that point, intensive discussion should be continued regarding how social systems can make full use of the potential of blockchain, while conducting R&D and proof of concept experiments with the coo peration of Social Science and Humanity. It is also imperative that Blockchain -related communities work together from global and long-term perspective, as were done to foster the Internet by all aro

- PDF页17：ckchain and the GDPR ”、” Blockchain for Government and Public Services ”等の質の高いレポートを発行している。 Digital Single Market も 2017 年の中間評価でブロックチェーンに関連づけられた。他にも、 ” Horizon Prize on Blockchains for Social Good ”や暗号資産に関するプロジェクトもイニシア ティブの下で開発が進められている。 Wien 工科大学の Matteo Maffei 教授が率いる研究グループが、Ethertrust プロジェクトによ り、Ethereum のスマートコントラクトのセキュリティーを向上させる研究成果を 2017 年 11 月 末に発表した。スウェーデンのチャルマース工科大学（Chalmers University of Technology）で は、公平なモビリティサービスに向けたMaaS（Mobility as a Service）におけるブロックチェー ン技術の役割について研究している。 フィンランドのAalto 大学は、Pekka Nikander 教授をリー 7 PoA では、トランザクションとブロックは、バリデーターと呼ばれる承認済みのアカウントによって検証される。

- PDF页36：共同の研究開発基盤をブロッ クチェーン専用に構築するのが望ましい。そうすることで社会基盤に要求されるセキュリティー 要件に対する安全性評価の研究も行うことができる。実際には、研究成果の蓄積と再利用が促進 できるように競争的資金も準備して研究開発のファンディングも必要と考える。 図 4.2 Bsafe.network ４.２ わが国の国家的社会基盤への適用 わが国では、2019 年に行政の手続きをワンストップ化する通称「デジタル手続き法案」が成立 した。 また、 安倍首相は、 信頼ある自由なデータ流通としてDFFT（Data Free Flow with Trust） 構想について、ダボス会議（2019 年 1 月 23 日）や G20 大阪サミット（2019 年 6 月 29 日）で 世界に提唱した。どちらも今後は、生産性向上やイノベーションにおいて、デジタルデータの活 用と流通がキーであり、改ざん、プライバシー、データ保護などのセキュリティーに関わる課題 の対処が必要であると提言した。ブロックチェーン技術はこれらの課題に対するソリューション を提供することが可能である。 14 ここで直接、間接的に生み出された成果として Unix, TCP/IP, DNS, WWW, HTTP などが挙げられる。

## T10_预见与优先领域

未自动命中；需人工按目录复核。
