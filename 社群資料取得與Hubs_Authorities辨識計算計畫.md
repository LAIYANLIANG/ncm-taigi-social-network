# 社群資料取得與 Hubs / Authorities 辨識計算計畫

> **專題題目**：「台語：從世代傳承的困境，到海外社群的隱形連結」  
> **方法論來源**：[`網路社群資料取得方法與技術.pdf`](網路社群資料取得方法與技術.pdf)（共 28 頁）  
> **理論與演算法來源**：[`課本_文字/14_Link_Analysis_and_Web_Search.md`](../課本_文字/14_Link_Analysis_and_Web_Search.md)（Ch 14）、[`03_Strong_and_Weak_Ties.md`](../課本_文字/03_Strong_and_Weak_Ties.md)（Ch 3）、[`04_Networks_in_Their_Surrounding_Contexts.md`](../課本_文字/04_Networks_in_Their_Surrounding_Contexts.md)（Ch 4）、[`05_Positive_and_Negative_Relationships.md`](../課本_文字/05_Positive_and_Negative_Relationships.md)（Ch 5）、[`13_The_Structure_of_the_Web.md`](../課本_文字/13_The_Structure_of_the_Web.md)（Ch 13）、[`19_Cascading_Behavior_in_Networks.md`](../課本_文字/19_Cascading_Behavior_in_Networks.md)（Ch 19）、[`20_The_Small_World_Phenomenon.md`](../課本_文字/20_The_Small_World_Phenomenon.md)（Ch 20）  
> **主計畫文件**：[`期末專題規劃_台語世代傳承與海外隱形連結.md`](期末專題規劃_台語世代傳承與海外隱形連結.md)

---

## 第一章：研究設計總覽——如何把「社群資料採集技術」與「課本網路理論」結合？

要將題目「台語：從世代傳承的困境，到海外社群的隱形連結」從概念推論推進到**實證網路分析（Empirical Social Network Analysis）**，必須同時解決兩個問題：**資料從哪裡合規、低偏差地取得？** 以及 **抓回來的文字與互動如何轉化為課本中的「節點、有向邊、Authorities 與 Hubs」？**

### 1.1 雙軸觀測邏輯：本土世代斷層 vs. 海外隱形連結

| 研究軸線 | 網路現象與待驗證命題 | 社群資料上的可觀測痕跡（Data Traces） | 對應課本理論與 PDF 技術 |
|---|---|---|---|
| **上篇｜台灣本地世代傳承困境** | 傳統台語權威與年輕世代網路之間存在**結構斷裂**，或因雙語相容性過高造成「滲透淘汰（Infiltration）」與同溫層封閉。 | 1. 論壇與影音平台上「家庭斷語痛點」討論的立場與情緒分布。<br>2. 傳統台語內容創作者與年輕台文／Podcast 社群在**共引矩陣 $M^T M$** 上呈現雙峰分離（少有交集的 Hub 連結兩端）。<br>3. 某些台語社群僅靠少數高中心性守門人維繫，聚集係數過高但跨世代流量萎縮。 | 課本 Ch 19.3（Dense Clusters）、Ch 19.7B（Bilingualism）、Ch 14.5（Authority 消長）<br>PDF p. 8–9（社群發現與時間切片）、p. 19–27（群聚係數與退化指標） |
| **下篇｜海外社群的隱形連結** | 地理分散的海外台語人士透過**弱連結橋樑（Local Bridges）**、**焦點閉合（Focal Closure）**與**社群媒體被動參與**，形成低頻接觸卻高效率的小世界互助網。 | 1. 海外台灣同鄉會、台語教會、Reddit／Threads／YouTube 上的跨國轉發、推薦連結與回覆樹。<br>2. **高 Hub 分數 + 高中介中心性（Betweenness），但低粉絲數／低 In-degree** 的「資訊二傳手／跨海策展帳號」——這正是「隱形連結」的實體節點。 | 課本 Ch 3.2, 3.4, 3.5（Weak Ties & Passive Engagement）、Ch 4.3（Affiliation）、Ch 14.2（Hubs & Authorities）、Ch 20（Small World）<br>PDF p. 7–8（中心性指標與二部圖投影） |

### 1.2 結合《網路社群資料取得方法與技術》的三層次社群定義（PDF p. 7）

依據 `網路社群資料取得方法與技術.pdf` 第 7 頁，在進入抓資料與演算法之前，必須先由外而內確立本專題對「台語社群」的三層操作性定義：

1. **第一層｜表面定義（場域與主題標籤邊界）**：  
   依據平台看板與標籤劃分研究場域（例如 PTT `TW-language` / `Gossiping` / `WomenTalk`、Reddit `r/Taiwan` / `r/ohtaigi`、YouTube 台語頻道生態、Threads/FB 公開台語貼文、海外同鄉會與台語教會公開網站）。*限制*：若只看單一場域，極易將「偶爾湊熱鬧的路過帳號」誤判為核心成員。
2. **第二層｜質化與文化認同定義（Rheingold 虛擬社群 & Anderson 想像共同體）**：  
   真正的台語核心與海外社群具備三個特徵：**共同關注焦點**（對應課本 Ch 4.3 *Foci*）、**長期持續互動**，以及**圈內專屬語言與拼寫暗號**（如台羅拼音 `Tâi-lô`、白話字 `POJ`、台文漢字用字、海外台灣同鄉會活動詞彙）。使用這套圈內詞彙，即可區分「外部評論者」與「真實文化社群成員」。
3. **第三層｜圖論與結構定義（Newman & Girvan 模組度 $Q$ 與 Ch 13–14 有向連結圖）**：  
   將每個帳號、頻道、網站或主題貼文視為**節點（Node）**，將引用、轉發、@提及、說明欄超連結與正向留言共現視為**有向邊（Directed Edge）**。在整體圖譜中，內部連線極度密集、對外連線相對稀疏的子圖即為真實「社群（Community Structure）」，再以課本 Ch 14 的 **HITS 演算法** 精準區分 **Authorities（核心意見領袖）** 與 **Hubs（資訊集散節點）**。

---

## 第二章：資料取得方法、渠道選型與防坑工程管線（對應 PDF pp. 1–18）

為兼顧期末專題的**合法合規性、低成本與學術可重現性**，本計畫採用 PDF 建議的「**官方 API + 靜態 HTML 低頻爬蟲 + 搜尋引擎間接索引**」混合採集架構，刻意避開高封號風險與高代理 IP 成本的 Meta 登入牆硬爬（PDF p. 12, 15）。

### 2.1 解決「網絡邊界設定偏差（Boundary Specification Problem）」的多層關鍵字字典

PDF 第 9 頁與第 18 頁明確指出：**「若只用官方全名（如單搜『台語』），樣本會被新聞媒體與政治口水洗版，漏掉真正的核心社群。」** 因此在採集前必須設計四層布林檢索（Boolean Search）與領域詞庫（NER Dictionary）：

| 詞庫層級 | 核心關鍵字設計（含繁中、台羅／白話字、英文） | 偵測目的與對應研究軸線 |
|---|---|---|
| **L1｜大眾通稱層** | `("台語" OR "臺語" OR "台灣話" OR "臺灣話" OR "閩南語")` | 捕捉一般大眾對台語的宏觀聲量與態度基準線。 |
| **L2｜核心台文／圈內暗號層** | `("Tâi-gí" OR "Tâi-gú" OR "Tâi-bûn" OR "台羅" OR "白話字" OR "Pe̍h-ōe-jī" OR "台文" OR "ChhoeTaigi" OR "iTaigi" OR "公視台語台")` | 濾除泛政治新聞，精準鎖定**核心文化實踐者、數位教材使用者與真鐵粉**（PDF p. 9 前提二）。 |
| **L3｜世代傳承痛點層** | `("台語" AND ("不會講" OR "聽得懂不會說" OR "母語傳承" OR "阿公阿嬤" OR "雙語家庭" OR "母語斷層" OR "本土語" OR "台語共學"))` | 專攻**上篇：世代傳承困境**，蒐集跨世代協調賽局困境與資訊瀑布案例。 |
| **L4｜海外隱形連結層** | `("Taiwanese Hokkien" OR "Taigi" OR ("台語" AND ("海外" OR "留學" OR "美國" OR "日本" OR "歐洲" OR "同鄉會" OR "教會" OR "台語禮拜" OR "FAPA")))` | 專攻**下篇：海外社群隱形連結**，捕捉跨國焦點（Foci）與弱連結橋樑。 |

### 2.2 四大資料渠道、技術選型與防爬蟲合規對策（依據 PDF pp. 1–16 事前偵察四步驟）

在撰寫爬蟲前，先依 PDF p. 10–11 執行「事前偵察四步驟」（檢查 `robots.txt` / `sitemap.xml`、檢視原始碼確認靜態或動態、辨識 WAF、無痕模式確認 Auth Wall 公開邊界），再決定各渠道最佳技術路徑：

| 目標渠道 | 涵蓋族群與研究角色 | 採集技術路徑（PDF 章節對照） | 可擷取的圖論邊與欄位 | 成本與合規風險控制 |
|---|---|---|---|---|
| **渠道 A｜YouTube 影音生態** | 橫跨本土年輕教學者、Podcast 轉載頻道、台語音樂與海外台語創作者（長尾市場，Ch 18.5） | **路徑一：YouTube Data API v3**（PDF p. 1）<br>透過 `search.list`、`videos.list`、`commentThreads.list` 抓取結構化 JSON。 | **節點**：頻道 ID、影片 ID、去識別化留言帳號。<br>**有向邊**：(1) 頻道說明欄推薦／引用其他頻道連結；(2) 留言者 $\to$ 頻道／影片；(3) 留言回覆樹（`parentId`）。 | **免費**（每日 10,000 units 配額足夠中小型專題使用），合規性最高。 |
| **渠道 B｜深度討論論壇（PTT 網頁版 & Reddit）** | **PTT**（`TW-language`, `Gossiping`, `WomenTalk`）：台灣青壯世代深度長文與歷史時間序列。<br>**Reddit**（`r/Taiwan`, `r/languagelearning`, `r/taiwanese`）：海外台裔與跨國學習者。 | **路徑二：靜態 HTML 解析 + 公開 JSON 端點**（PDF p. 1, 11）<br>PTT 網頁版使用 `httpx` + `BeautifulSoup`；Reddit 直接在討論串網址後方加上 `.json` 或用 PRAW API。 | **節點**：帳號 ID（雜湊後）、看板／文章 ID。<br>**有向邊**：推噓文回覆關係、引用原文（`※ 引述`）、跨看板共同活躍用戶的二部圖投影。 | **免費**。遵循 PDF p. 11–12：**單執行緒、隨機延遲 Jitter 3–10 秒、從看板列表頁進入、不使用站內搜尋端點**。 |
| **渠道 C｜即時社群（Threads / FB 公開粉專 / IG）** | **Threads**：台灣年輕世代與海內外即時共鳴。<br>**FB 公開粉專／海外同鄉會公開頁**：35 歲以上與海外組織骨幹。 | **路徑五：搜尋引擎間接索引法**（PDF p. 2, 11, 15）<br>利用 `site:threads.net`、`site:facebook.com` 搭配 Google Custom Search API 或 SerpApi，避免直接用私人帳號 Cookie 登入硬爬。 | **節點**：公開帳號／粉專網址、主題標籤（Hashtag）。<br>**有向邊**：同貼文摘要／轉貼提及之共現關係、跨平台網址引流連結（如 Threads 引流至 YouTube / 台語辭典）。 | **免費試用額度或極低成本**（PDF p. 14：Google Cloud 試用額度或 SerpApi；絕對避免 PDF p. 15 警告的「私帳 Cookie 被永久停權」風險）。 |
| **渠道 D｜海外台灣組織與台語數位資源網（Web Graph）** | 各地台灣同鄉會、台語長老教會網站、開源台文／辭典生態（ChhoeTaigi、萌典、iTaigi、阿勇台語等）。 | **路徑二：靜態超連結爬蟲（1–2 層廣度優先搜尋 BFS，對應 Ch 2.3）**<br>檢查 `robots.txt` 後，抓取各網站「友站連結 / 學習資源推薦頁」的 `<a href>` 外連。 | **節點**：網域／組織網站。<br>**有向邊**：網頁超連結 $u \to v$（與課本 Ch 14.2 Fig. 14.1–14.5 完全同構的標準 Web 圖譜）。 | **免費**，請求量極小（數百頁內即可收斂）。 |

### 2.3 資料品質檢核與「自適應停止準則（Adaptive Stopping Criterion, PDF pp. 20–22）」

抓資料不能無止境擴張，也不該憑感覺決定「夠不夠」。依據 PDF 第 20–22 頁的數學判準，於採集管線中內建三個停止與過濾機制（前提：採隨機／時間分層抽樣，而非只抓演算法 Top Posts 排序，避免 PDF p. 22 前提二偏差）：

1. **資訊飽和曲線與希普斯定律（Heaps' Law, PDF p. 20–21）**：  
   隨著累計抓取語料總字數 $N$ 增加，不重複主題關鍵字／詞彙數 $V(N)$ 服從次線性成長 $V(N) = K \cdot N^\beta$（$\beta \in [0.4, 0.6]$）。每批次（例如每新增 500 則貼文／留言）計算邊際資訊增益坡度 $\frac{\Delta V}{\Delta N}$；當連續三個批次的新詞彙成長率低於預設閾值（例如 $< 1\%$）且低於理論預測坡度，表示該平台在該關鍵字群組已達**理論飽和（Theoretical Saturation）**，即可停止擴張抓取。
2. **信噪比邊際變化率（Marginal Signal-to-Noise Slope, PDF p. 21）**：  
   定義每批資料的「有效訊號率」（排除純貼圖、機器人廣告、無關諧音梗或純政治謾罵後的實質語言討論比例）。當擴張到新看板（例如從 `TW-language` 擴張到 `Gossiping` 某熱議政治串）導致整體樣本的邊際品質坡度**由正轉負（跌破零軸）**時，立刻截斷該雜訊來源或收緊 L2/L3 關鍵字條件。
3. **樣本種類廣度——香農資訊熵（Shannon Diversity Index / Entropy, PDF p. 21）**：  
   將樣本依「**來源平台 $\times$ 場域屬性（本土世代 vs. 海外跨國）**」劃分為 $C$ 個類別，計算各類別比例 $p_i$ 與資訊熵：
   $$H = -\sum_{i=1}^{C} p_i \ln p_i, \qquad H_{\text{norm}} = \frac{H}{\ln C} \in [0, 1]$$
   若 95% 資料全來自單一平台（如只有 PTT），$H_{\text{norm}} \to 0$，結論必將嚴重偏向單一世代；必須透過配額採樣確保 $H_{\text{norm}}$ 維持在較高水準（例如 $\ge 0.70$），讓本土論壇、年輕影音與海外社群維持均衡代表性。
4. **工程防禦與隱私合規（PDF p. 3, 12, 18）**：  
   - **軟封鎖（Soft Block）偵測與斷點續傳**：檢查 HTTP 200 回傳內容長度與驗證碼字樣，觸發異常即指數退避（Backoff）休息，資料即時寫入本地 SQLite。  
   - **個資去識別化（PII Masking）**：資料寫入 SQLite 的第一時間，以鹽值雜湊（Salted SHA-256）轉換所有 `author_id`（保留同一帳號在不同貼文下的**可連結性與跨場域共現識別能力**，同時徹底保護個人隱私）。

---

## 第三章：核心意見領袖（Authorities）與關鍵資訊集散節點（Hubs）的定義與網路建構

### 3.1 為什麼不能只算「按讚數、訂閱數或 In-Degree」？

在課本 **Ch 14.2（[`14_Link_Analysis_and_Web_Search.md`](../課本_文字/14_Link_Analysis_and_Web_Search.md), pp. 353–355, Fig. 14.1）** 中，Easley & Kleinberg 用搜尋 `"newspapers"` 的經典例子指出：如果只計算「收到多少入連結（In-degree voting）」，真正專業的報紙（*New York Times*, *USA Today*）雖然票數高，但 **Yahoo!、Facebook、Amazon** 這類「任何議題都會被順便連到」的泛用型超大平台也會拿到一樣高的票數。

套用到台語社群研究中，會發生完全相同的陷阱：
- 如果只看「討論台語的貼文按讚數或被提及數（In-degree）」，排名最高的往往是**偶爾拍一支台語搞笑片的百萬娛樂網紅**，或是**在選舉期間順帶提及台語政策的主流政治人物**；
- 真正深耕台語教學、維繫海外台灣人跨國認同、以及在社群之間默默整理資源並轉發的關鍵節點，反而會被一般聲量淹沒！

因此，必須引入課本 Ch 14.2 的 **「雙重角色互相增強（Principle of Repeated Improvement）」** 框架：

1. **Authorities（核心意見領袖／權威內容源）在本專題的意義**：  
   產出高純度台語文化內容、辭典工具、語言教學、深度世代論述或海外社群組織核心，並且**受到眾多「高水準策展者／轉發者（Hubs）」共同推薦、引用或持續互動背書**的節點。  
   *實例*：台語開源辭典與工具（ChhoeTaigi、萌典）、長期產出優質內容的台語 Podcast／YouTube 頻道、特定海外台灣同鄉會或台語教會的核心主辦單位、PTT `TW-language` 資深語料／考據發文者。
2. **Hubs（關鍵資訊集散節點／跨群策展與轉發樞紐）在本專題的意義**：  
   本身不一定是流量最大或產出最多原創內容的明星，但扮演**「優質資源清單整理者（High-value Lists）」、「知識轉譯與搬運工」、「跨平台引流節點」或「跨海弱連結橋樑」**。他們準確知道哪裡有好的台語資源與討論（指向多個高品質 Authorities），並把資訊聚攏、轉發給不同圈層的受眾。  
   *實例*：整理「海外小孩學台語必看頻道／網站懶人包」的部落格與 Threads 串文帳號、把台灣本土台語新聞／創作轉貼到 Reddit `r/Taiwan` 或海外社團的橋樑帳號、在 PTT 與 YouTube 多個台語頻道下頻繁留下建設性補充並附參考連結的「超級策展型用戶」。

### 3.2 四種圖譜建構方式：如何從抓到的資料定義「有向邊 $i \to j$」？

因為不同社群平台機制不同，我們將採集到的資料依以下四種規則轉化為有向加權圖 $G = (V, E)$ 與鄰接矩陣 $M$（其中 $M_{ij} = w_{ij} \ge 0$ 代表節點 $i$ 指向節點 $j$ 的背書權重）：

#### 設計 1｜顯性引用與轉發有向圖（Web / YouTube 頻道 / 社群轉發）
- **適用資料**：渠道 D（台語資源／海外社團網頁超連結）、渠道 A（YouTube 影片說明欄推薦的相關頻道或外部字典連結）、渠道 C（Threads / X 公開轉發與 @引用）。
- **建邊規則**：若節點 $i$ 轉發、引用或以超連結指向節點 $j$（且排除自己連自己 $i \neq j$），建立有向邊 $i \to j$，權重 $w_{ij}$ 為引用次數或 $\log(1 + \text{次數})$。
- **語意**：**$i$ 是投票者／推薦清單（潛在 Hub），$j$ 是被推薦／引用的資源（潛在 Authority）**。

#### 設計 2｜「用戶 $\times$ 創作者／貼文」二部圖直跑 HITS（PTT / YouTube 留言區 / Reddit）
- **理論依據**：PDF p. 8 指出匿名論壇或留言區沒有明確好友追蹤機制，需建構「用戶－貼文」二部圖；而對照課本 Ch 14.2 (Fig. 14.1–14.5)，**標準 HITS 模型本質上就是在「左部清單頁（Hubs）$\to$ 右部權威頁（Authorities）」的二部有向圖上運作！**
- **建邊規則**：設左部為所有不重複活躍用戶 $U$，右部為台語創作者頻道或深度主題文章 $P$。當用戶 $u \in U$ 在創作者／文章 $p \in P$ 下進行**實質正向互動**（如推文認同、有效提問與討論補充），建立有向邊 $u \to p$（此時 $M$ 可寫成 $|U| \times |P|$ 矩形矩陣，或在 $(|U|+|P|) \times (|U|+|P|)$ 方陣中僅右上角區塊非零）。
- **直覺解釋**：
  - 若用戶 $u$ 只在 1 篇熱門八卦文底下留一句「推」，他對每個物件的貢獻極低；
  - 若用戶 $u$ **橫跨 8 個不同但優質的台語教學頻道／海外社團文章持續互動**，HITS 會給予 $u$ 極高的 **Hub 分數**；而**同時被大量這類高 Hub 鐵粉與策展人共同互動的創作者 $p$**，就會脫穎而出獲得極高的 **Authority 分數**！

#### 設計 3｜二部圖投影共現網路與濾除「演算法偽社群雜訊」（PDF p. 8–9）
- 在分析平台內部聚落時，從二部圖的關聯矩陣 $B$（$|U| \times |P|$）可自然導出兩個課本核心矩陣：
  1. **創作者／權威共引矩陣 $C_{\text{auth}} = B^T B$**：$C_{p_1, p_2}$ 代表同時被同一批用戶背書／學習的兩位創作者或資源，用來**發現台語內容是否分裂成「本土傳統圈」與「年輕數位／海外圈」兩大無交集聚落**。
  2. **用戶共現矩陣 $C_{\text{user}} = B B^T$**：$C_{u_1, u_2}$ 代表兩位用戶在多少個相同台語場域交會（對應課本 Ch 4.3 *Focal Closure*）。
- **濾除偽社群雜訊（PDF p. 9 前提三）**：在 Threads 或 YouTube 演算法推播下，陌生人可能剛好在同 1 支百萬爆紅短片底下留言。因此必須設定**最低互動門檻 $\tau$**（例如只保留與目標主題互動次數 $\ge 3$ 篇／支的節點，或投影邊須滿足共現數 $\ge \tau$ 且以 Cosine / Jaccard 相似度正規化），才能把「演算法路人」洗掉，留下真實的隱形社群骨架。

#### 設計 4｜符號網路過濾（Signed Network Filtering，結合 PDF p. 9 前提一 & 課本 Ch 5）
- **致命陷阱**：PTT 八卦板、Threads 或新聞留言區常出現「言語政策吵架／出征互罵」。如果某篇釣魚引戰文引來 500 則對罵留言，純無號圖論會誤把這篇引戰文算成最高 Authority，把互相攻擊的雙方畫進同一個「密集社群」！
- **解決方案**：依據 PDF p. 9 與課本 Ch 5（Positive and Negative Relationships），在建邊前先做立場與情緒標記（如 PTT 區分「推 `(+)`」與「噓 `(-)`」，YouTube/Threads 透過情緒與台語認同字典或輕量分類器標記正向支持 `+1` vs. 負向攻擊 `-1`），將網路拆為：
  - **正向背書矩陣 $M^+$**：專門用來計算 **HITS（Authorities 與 Hubs）** 及 **Louvain/Leiden 正向合作社群**；
  - **負向衝突矩陣 $M^-$**：用來檢驗課本 Ch 5 的**結構平衡（Structural Balance）**——觀察台語社群在公共議題上是否與外部批判者呈現兩極化對立結構。

---

## 第四章：Authorities 與 Hubs 的數學辨識與關聯計算步驟

本章嚴格對應課本 **Ch 14.2（pp. 355–358）** 與 **Ch 14.6A（pp. 368–375）** 的矩陣與譜分析推導，並進一步設計「如何計算 Hubs 與 Authorities 之間的關聯結構」之量化指標。

### 4.1 HITS 演算法數學計算流程

設正向背書有向網路共有 $n$ 個節點，其加權鄰接矩陣為 $M \in \mathbb{R}_{\ge 0}^{n \times n}$，其中 $M_{ij} = w_{ij}$ 表示節點 $i$ 指向（推薦／引用／正向互動）節點 $j$ 的權重。定義每個節點的 Authority 分數向量 $\mathbf{a} \in \mathbb{R}^n$ 與 Hub 分數向量 $\mathbf{h} \in \mathbb{R}^n$：

1. **初始化（Initialization, $k = 0$）**：
   $$a_i^{(0)} = 1, \quad h_i^{(0)} = 1 \qquad (\forall i = 1, \dots, n)$$
2. **反覆更新（Iterative Update, 第 $k$ 步）**：
   - **Authority 更新規則（課本 Eq. 14.2, p. 370）**：節點 $i$ 的權威分數，等於所有指向它的節點 $j$ 的 Hub 分數加權總和：
     $$a_i^{(k)} \leftarrow \sum_{j=1}^{n} M_{ji} h_j^{(k-1)} \quad \Longleftrightarrow \quad \mathbf{a}^{(k)} \leftarrow M^T \mathbf{h}^{(k-1)}$$
   - **Hub 更新規則（課本 Eq. 14.1, p. 369）**：節點 $i$ 的樞紐分數，等於它所指向的所有節點 $j$ 的 Authority 分數加權總和：
     $$h_i^{(k)} \leftarrow \sum_{j=1}^{n} M_{ij} a_j^{(k)} \quad \Longleftrightarrow \quad \mathbf{h}^{(k)} \leftarrow M \mathbf{a}^{(k)}$$
3. **正規化（Normalization, p. 357）**：  
   為避免分數隨迭代次數指數膨脹，每步計算後皆進行正規化（課本 p. 357 採用 $L_1$ 總和歸一化使總和為 $1$，實務數值運算亦可採用 $L_2$ 範數歸一化，兩者方向向量等價）：
   $$\mathbf{a}^{(k)} \leftarrow \frac{\mathbf{a}^{(k)}}{\|\mathbf{a}^{(k)}\|_1}, \qquad \mathbf{h}^{(k)} \leftarrow \frac{\mathbf{h}^{(k)}}{\|\mathbf{h}^{(k)}\|_1}$$
4. **收斂判斷與譜分析性質（課本 Ch 14.6A, pp. 370–375）**：  
   重複步驟 2–3，直到前後兩步的變化量 $\|\mathbf{a}^{(k)} - \mathbf{a}^{(k-1)}\|_1 + \|\mathbf{h}^{(k)} - \mathbf{h}^{(k-1)}\|_1 < 10^{-8}$。  
   由課本推導可知：
   $$\mathbf{a}^{(k)} \propto (M^T M)^{k-1} M^T \mathbf{h}^{(0)}, \qquad \mathbf{h}^{(k)} \propto (M M^T)^k \mathbf{h}^{(0)}$$
   在連通性良好（主特徵值嚴格大於次大特徵值 $|c_1| > |c_2|$）的網路中，無論初始向量為何，極限分數 $\mathbf{a}^*$ 與 $\mathbf{h}^*$ 必分別收斂至對稱矩陣 **$M^T M$** 與 **$M M^T$** 的**主特徵向量（Principal Eigenvector）**——完全由網路連結結構本身決定。

> **實務提醒（單一超強同溫層霸榜問題）**：HITS 具備「Tightly Knit Community (TKC) Effect」，若某個無關的政治大群聚內部互相轉發極多，主特徵向量可能被該單一聚落佔據。因此實務上必須：(a) 確認輸入圖已通過第二章 L1–L4 關鍵字與符號過濾；(b) 若存在多個明顯獨立的次社群（如「本土台語圈」vs.「海外台語圈」），**先用 Leiden/Louvain 偵測社群後，同時計算「全網全域 HITS」與「各次社群內部 HITS」**。

---

### 4.2 如何辨識並量化「Authorities 與 Hubs 之間的關聯結構」？

算出每個節點的 $(a_i^*, h_i^*)$ 只是第一步；真正能回答本專題「世代傳承困境」與「海外隱形連結」的關鍵，在於以下 **五種關聯分析方法**：

#### 方法 1｜節點角色四象限矩陣（Authority–Hub Typology）
以全體節點的 $\log(a_i^* + \epsilon)$ 與 $\log(h_i^* + \epsilon)$ 的中位數或特定百分位（如 Top 10% / 第 75 百分位）作為門檻，將網路成員精準劃分為四類角色：

| 象限分類 | 指標特徵 | 台語社群中的真實角色 | 在專題中的意義 |
|---|---|---|---|
| **Q1｜雙棲超級領袖（Dual Leaders）** | High $a_i^*$, High $h_i^*$ | 既產出高權威內容，又積極推薦/串聯同好的節點（例如：主動訪談跨國講者並整理資源清單的台語 Podcast、海外台語文化協會官網）。 | **生態系引擎**：同時決定內容深度與擴散廣度。 |
| **Q2｜純核心意見領袖（Core Authorities）** | High $a_i^*$, Low $h_i^*$ | 字典資料庫、官方教材、資深學者或專注創作的傳統台語 KOL（被大家指向，但本身極少外連或轉發他人）。 | **文化存量庫**：若只剩 Q2 而缺乏 Q4 串聯，就會陷入「有資源但年輕世代或海外找不到」的困境。 |
| **Q4｜純資訊集散樞紐（Pure Hubs / Curators）** | Low $a_i^*$, High $h_i^*$ | 資源整理懶人包帳號、跨平台搬運工、活躍的海外台語學習志工、跨多頻道留言推薦的資深用戶。 | **隱形連結的實踐者**：他們沒有高粉絲數，卻是把 Q2 權威介紹給邊陲受眾的關鍵通道！ |
| **Q3｜邊陲參與者（Periphery）** | Low $a_i^*$, Low $h_i^*$ | 偶爾互動的學習者、潛水閱聽眾（對應課本 Ch 20.6 Periphery）。 | 觀察邊陲是否能透過 Q4/Q1 進入核心，避免海外二三代徹底失聯。 |

#### 方法 2｜Hub–Authority 跨社群橋接指標（Cross-Community BridgeHub Score）
為直接找出「打通台灣本土與海外社群」或「跨接不同世代圈層」的關鍵 Hubs，結合 PDF p. 8 的 **Leiden / Louvain 社群發現演算法**（將全圖依模組度最大化分為社群集合 $\{C_1, C_2, \dots, C_m\}$，或依節點屬性標記「本土社群 $C_{\text{local}}$」與「海外社群 $C_{\text{diaspora}}$」），定義每個樞紐節點 $i$ 對某個社群 $C_r$ 的權威背書貢獻度為：
$$S(i \to C_r) = \sum_{j \in C_r} M_{ij} a_j^*$$
接著計算節點 $i$ 的 **跨界樞紐熵（Cross-Community Hub Entropy）** 與 **本土—海外雙向橋接分數（BridgeHub Score）**：
1. **跨本土—海外雙向橋接分數**：
   $$\text{BridgeHub}(i) = \sqrt{S(i \to C_{\text{local}}) \cdot S(i \to C_{\text{diaspora}})}$$
   只有當節點 $i$ **同時連結台灣本土高權威資源與海外社群高權威節點**時，$\text{BridgeHub}(i)$ 才會高（幾何平均確保缺一不可）。
2. **跨聚落多樣性熵（Bridging Entropy）**：設 $q_{ir} = \frac{S(i \to C_r)}{\sum_{l=1}^m S(i \to C_l)}$，則：
   $$\text{HubDiversity}(i) = -\sum_{r=1}^{m} q_{ir} \ln q_{ir}$$
   $\text{HubDiversity}(i)$ 越高，代表這個 Hub 跨越越多不同世代或地域的台語同溫層，正是課本 Ch 3.5 **結構洞跨越者（Structural Hole Spanner）** 的量化指標！

#### 方法 3｜「隱形連結」的多指標對照識別（HITS × PageRank × Betweenness × In-Degree）
結合課本 **Ch 3.6（Betweenness）**、**Ch 14.3（PageRank）** 與 PDF **pp. 7–8（中心性指標）**，建立以下指標交叉對照矩陣，專門用來抓出「表面聲量小、但結構位置極關鍵」的節點：

| 指標組合特徵 | 對應理論與 PDF 頁碼 | 辨識出的社群現象 |
|---|---|---|
| **高 In-Degree + 低 Authority** | Ch 14.2 Fig. 14.1（Yahoo!/Amazon 效應） | **偽權威／泛流聲量節點**：例如偶爾提到台語的政治新聞粉專或娛樂大網紅，雖然聲量高，但背書來源多為一次性路人，並非台語核心 Hubs 認可的對象。 |
| **高 Authority + 高 PageRank** | Ch 14.2 & 14.3 | **全域共識型意見領袖**：既受核心策展者推薦，也在整個資訊流隨機漫步中居核心地位（例如核心台語辭典或跨圈指標頻道）。 |
| **高 Hub + 高 Betweenness + 低/中 In-Degree** | Ch 3.2, 3.6 & PDF p. 7–8 | **「隱形連結」關鍵二傳手（Invisible Link Bridges）**：這類節點通常低調、自己很少成為話題中心，但在最短路徑與資訊聚合上不可或缺，切斷他們會導致海外社群與本土核心斷鏈！ |
| **極高 Clustering Coefficient + 低跨群 Hub 分數** | Ch 3.5, Ch 19.3 & PDF p. 8, 27 | **封閉孤島同溫層**：內部互相吹捧但外部資訊打不進去，若無雙語緩衝區（Ch 19.7B）或外部 Hubs 橋接，新世代極難加入。 |

#### 方法 4｜二跳關聯結構分析：$M^T M$（權威共現）與 $M M^T$（樞紐同盟）
直接檢視課本 Ch 14.6A 的兩個核心對稱矩陣：
- **權威共引圖 $W_{\text{auth}} = M^T M$**：兩個意見領袖 $j_1, j_2$ 在 $W_{\text{auth}}$ 中的邊權重越高，代表越多相同的 Hubs 同時推薦他們。對 $W_{\text{auth}}$ 跑 Leiden 社群分群，可直接檢驗**「傳統世代台語權威」與「新世代／海外數位台語權威」之間是否存在明顯的共引斷層**！
- **樞紐同盟圖 $W_{\text{hub}} = M M^T$**：找出指向同一群台語 Authorities 的 Hubs，驗證海外跨國組織（如不同城市的同鄉會、教會或跨國論壇策展者）是否在底層共享同一套「精神與知識權威源頭」。

---

## 第五章：時間演化、早期預警與社群存活分析整合（對應 PDF pp. 19–28）

為了呼應 PDF 後半部極具深度的「觀未兆（生於毫末）」、「失道而後禮」與「時間切片存活分析」，同時結合課本 **Ch 14.5（Fig. 14.9–14.10 權威動態消長）**，本計畫設計以下動態檢驗層：

1. **時間切片（Time-Slicing, PDF p. 9, 27）**：  
   將採集的 PTT 歷史文章與 YouTube 影片／留言依「季度」或「年度」切割為 $G^{(t)} = (V^{(t)}, E^{(t)})$，追蹤：
   - **世代權威轉移曲線 $a_i^*(t)$**：傳統電視／廣播／老牌板塊權威 vs. 新興台羅數位工具／Podcast／海外社群領袖之 Authority 分數消長（直接類比課本 p. 367 Fig. 14.9–14.10 美國最高法院判例權威消長曲線）。
2. **「社群活力／退化」拓撲聚合指標（Dimensional Reduction, PDF p. 27）**：  
   將每個時間切片 $t$ 的節點級指標壓縮為社群整體狀態純量：
   - **全域群聚係數 $C_{\text{global}}(t)$**（衡量同溫層封閉度）；
   - **Hub 分數與中介中心性的吉尼係數 $\text{Gini}_{\text{hub}}(t), \text{Gini}_{\text{betw}}(t)$**（PDF p. 27）：  
     $$\text{Gini}(\mathbf{x}) = \frac{\sum_{i=1}^n \sum_{j=1}^n |x_i - x_j|}{2 n \sum_{i=1}^n x_i}$$
     當 $\text{Gini}_{\text{hub}}(t)$ 急遽飆升且接近 $1$，表示整個社群的資訊集散功能被極少數「超級守門人／少數熱心版主」壟斷——一旦這幾位關鍵 Hub 停更或離開，社群就會面臨結構性崩解風險。
   - **語言制度化／防禦指標（對應 PDF p. 19–20「失道而後禮」）**：追蹤看板或留言區中「糾正用字／正字吵架／板規爭議」相對於「自然日常台語創作分享」的比例。當糾錯與規範爭議壓過自然交流，往往引發新手卻步（提高課本 Ch 19.7B 的雙語加入門檻 $c$！），形成語言傳承的負向臨界訊號。
3. **擴充至回溯對照與存活模型格式（PDF pp. 20, 24–28）**：  
   若能取得多個語言／地方性公開看板或社團（例如對比「成功轉型跨海連結的台語社團」vs.「已沉寂的地區性方言社團」），可依 PDF p. 28 轉換為 **Counting Process 長格式 `(community_id, start, stop, event, clustering_avg, hub_gini, bridge_ratio)`**，執行 Forward Fill 補值與 Z-score 標準化，檢驗「擁有多元化 Hubs 與跨界橋樑」是否顯著降低語言社群萎縮死亡的風險比率（Hazard Ratio）。

---

## 第六章：可直接執行的 Python 實作管線範本

以下範本整合了 **課本 Ch 14.2 / 14.6A 矩陣版 HITS**、**PageRank / Betweenness 對照**、**本土—海外 BridgeHub 辨識**、**四象限分類**、以及 **PDF 第 21 & 27 頁的 Shannon Entropy / Gini Coefficient 指標計算**（僅依賴常見 Python 資料科學套件 `numpy`, `pandas`, `networkx`）：

```python
import hashlib
import math
import numpy as np
import pandas as pd
import networkx as nx


# ---------------------------------------------------------
# 1. 合規去識別化與資料品質檢核（PDF p. 3, 18, 21）
# ---------------------------------------------------------
def hash_user_id(raw_id: str, salt: str = "taigi_project_salt") -> str:
    """PII Masking: 入庫前雜湊使用者帳號，保留跨貼文共現連結性但去識別化"""
    return hashlib.sha256(f"{salt}:{raw_id}".encode("utf-8")).hexdigest()[:16]


def shannon_entropy_normalized(counts: dict) -> float:
    """計算跨平台/跨地域類別分布的正規化香農資訊熵 H_norm in [0, 1]"""
    total = sum(counts.values())
    if total == 0 or len(counts) <= 1:
        return 0.0
    probs = [c / total for c in counts.values() if c > 0]
    h = -sum(p * math.log(p) for p in probs)
    return h / math.log(len(counts))


def gini_coefficient(values: np.ndarray) -> float:
    """計算中心性/Hub 分數之吉尼係數（PDF p. 27 壟斷與結構脆弱度指標）"""
    x = np.sort(np.asarray(values, dtype=float))
    if len(x) == 0 or np.sum(x) == 0:
        return 0.0
    n = len(x)
    idx = np.arange(1, n + 1)
    return float((2 * np.sum(idx * x)) / (n * np.sum(x)) - (n + 1) / n)


# ---------------------------------------------------------
# 2. 課本 Ch 14.2 & 14.6A：矩陣迭代法計算 HITS
# ---------------------------------------------------------
def compute_hits_matrix(G: nx.DiGraph, max_iter: int = 200, tol: float = 1e-8):
    """
    嚴格對應 Easley & Kleinberg Ch 14.2 & 14.6A (Eq. 14.1, 14.2):
      a^(k) <- M^T h^(k-1)  (Authority Update Rule)
      h^(k) <- M   a^(k)    (Hub Update Rule)
    採用 L1 正規化，使所有節點 Authority 總和 = 1、Hub 總和 = 1。
    """
    nodes = list(G.nodes())
    n = len(nodes)
    if n == 0:
        return {}, {}

    # M[i, j] = w_ij (節點 i 指向節點 j 的正向背書權重)
    M = nx.to_numpy_array(G, nodelist=nodes, weight="weight", dtype=float)

    h = np.ones(n, dtype=float)
    a = np.ones(n, dtype=float)

    for _ in range(max_iter):
        a_new = M.T @ h
        a_sum = a_new.sum()
        if a_sum > 0:
            a_new /= a_sum

        h_new = M @ a_new
        h_sum = h_new.sum()
        if h_sum > 0:
            h_new /= h_sum

        diff = np.abs(a_new - a).sum() + np.abs(h_new - h).sum()
        a, h = a_new, h_new
        if diff < tol:
            break

    auth_dict = {nodes[i]: float(a[i]) for i in range(n)}
    hub_dict = {nodes[i]: float(h[i]) for i in range(n)}
    return auth_dict, hub_dict


# ---------------------------------------------------------
# 3. 整合二部圖/有向圖過濾、角色四象限與跨海 BridgeHub 辨識
# ---------------------------------------------------------
def analyze_taigi_network(edges_df: pd.DataFrame, node_region: dict, min_weight: float = 1.0):
    """
    edges_df 欄位: ['source', 'target', 'weight', 'sentiment']
      - sentiment: +1 (正向背書/推薦/學習互動) 或 -1 (負向爭吵，會於計算 HITS 前濾除)
    node_region: {node_id: 'local' | 'diaspora' | 'resource'}
    """
    # Step A: 符號網路過濾 (Signed Network Filtering, PDF p. 9 & Ch 5)
    pos_df = edges_df[(edges_df["sentiment"] > 0) & (edges_df["weight"] >= min_weight)]

    # 聚合相同 (source, target) 的加權邊
    agg_df = pos_df.groupby(["source", "target"], as_index=False)["weight"].sum()

    G = nx.DiGraph()
    for _, row in agg_df.iterrows():
        if row["source"] != row["target"]:
            G.add_edge(row["source"], row["target"], weight=float(row["weight"]))

    # Step B: 計算 HITS (Ch 14.2), PageRank (Ch 14.3), Betweenness (Ch 3.6)
    auth, hub = compute_hits_matrix(G)
    pagerank = nx.pagerank(G, weight="weight") if len(G) > 0 else {}
    # 無向投影計算最短路徑守門人 Betweenness 與局部群聚係數
    G_undir = G.to_undirected()
    betweenness = nx.betweenness_centrality(G_undir, normalized=True) if len(G) > 0 else {}
    clustering = nx.clustering(G_undir) if len(G) > 0 else {}

    # Step C: 計算跨本土—海外橋接分數 BridgeHub(i) 與 Hub Diversity
    records = []
    for node in G.nodes():
        s_local = 0.0
        s_diaspora = 0.0
        s_resource = 0.0
        for _, nbr, edata in G.out_edges(node, data=True):
            w = edata.get("weight", 1.0)
            contrib = w * auth.get(nbr, 0.0)
            reg = node_region.get(nbr, "local")
            if reg == "local":
                s_local += contrib
            elif reg == "diaspora":
                s_diaspora += contrib
            else:
                s_resource += contrib

        bridge_local_diaspora = math.sqrt(s_local * s_diaspora)
        records.append({
            "node": node,
            "region": node_region.get(node, "unknown"),
            "in_degree": G.in_degree(node, weight="weight"),
            "out_degree": G.out_degree(node, weight="weight"),
            "authority": auth[node],
            "hub": hub[node],
            "pagerank": pagerank.get(node, 0.0),
            "betweenness": betweenness.get(node, 0.0),
            "clustering": clustering.get(node, 0.0),
            "bridge_local_diaspora": bridge_local_diaspora,
        })

    df = pd.DataFrame(records)
    if df.empty:
        return df, {}

    # Step D: 四象限角色分類 (以非零分數的第 75 百分位數作為核心門檻)
    a_pos = df.loc[df["authority"] > 0, "authority"]
    h_pos = df.loc[df["hub"] > 0, "hub"]
    a_thr = a_pos.quantile(0.75) if len(a_pos) else 0.0
    h_thr = h_pos.quantile(0.75) if len(h_pos) else 0.0

    def classify_role(row):
        is_a = row["authority"] >= a_thr and row["authority"] > 0
        is_h = row["hub"] >= h_thr and row["hub"] > 0
        if is_a and is_h:
            return "Q1_Dual_Leader"
        elif is_a:
            return "Q2_Core_Authority"
        elif is_h:
            return "Q4_Pure_Hub_Curator"
        return "Q3_Periphery"

    df["role"] = df.apply(classify_role, axis=1)

    # Step E: 全域社群健康度摘要 (PDF p. 27)
    summary = {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "global_clustering": nx.transitivity(G_undir),
        "hub_gini": gini_coefficient(df["hub"].values),
        "authority_gini": gini_coefficient(df["authority"].values),
        "region_entropy": shannon_entropy_normalized(df["region"].value_counts().to_dict()),
    }
    return df.sort_values(["authority", "hub"], ascending=False), summary
```

---

## 第七章：整合進期末報告的 4 個實戰步驟

1. **步驟一｜決定最小可行資料集（MVP Dataset，建議 1 週內完成）**：  
   不要一次抓 5 個平台！建議從 **「YouTube 台語生態（頻道＋留言二部圖）+ PTT `TW-language` / `Gossiping`（對照本土跨世代討論）+ Reddit `r/Taiwan` / 海外同鄉會與資源網站超連結」** 開始。這三個來源**完全不需要破解防爬蟲或登入牆**，卻正好同時覆蓋本土世代困境與海外隱形連結。
2. **步驟二｜進行去識別化清洗與符號過濾**：  
   套用第二章的 L1–L4 台語詞彙表與 PDF p. 21 的信噪比檢查、Shannon Entropy 檢核；濾除互罵與路人雜訊，保留具連續互動的節點。
3. **步驟三｜跑出 HITS 四象限與「隱形連結 Hub」實證清單**：  
   執行第六章的 Python 程式，找出：
   - 誰是高 Authority 的文化與語言源頭？（對比傳統媒體 vs. 數位台文工具）
   - 誰是高 `BridgeHub` 與高 `Betweenness`、但低 `In-Degree` 的「跨海隱形連結樞紐」？
   - 計算共引矩陣 $M^T M$，檢驗不同世代的台語內容是否出現斷裂聚落。
4. **步驟四｜寫入期末報告主體章節**：  
   將上述數據結果與視覺化網路圖放入 [`期末專題規劃_台語世代傳承與海外隱形連結.md`](期末專題規劃_台語世代傳承與海外隱形連結.md) 建議的「**第五章：實證資料與網路分析結果**」，再與「**Ch 19.7B 雙語緩衝區**」及「**Ch 20 小世界去中心化搜尋**」互證，即可完成兼具理論深度與數據實作的期末研究報告。
