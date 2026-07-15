# Shopping Cart Checkout

使用 **Python** 實作購物車結帳系統，支援**品類促銷、優惠券折扣**以及完整的結帳計算流程。

---

## 結算流程

購物車結帳依照以下順序進行計算：

1. 套用品類促銷
2. 計算促銷後商品總金額
3. 套用一張符合條件的優惠券
4. 四捨五入至小數點後兩位
5. 輸出最終結算金額

---

## 題目假設

- 優惠券於到期日當天仍可使用。
- 商品總額**等於**優惠券門檻時即可使用。
- 優惠券門檻以**套用品類促銷後**的商品總額判定。
- 同一品類於同一次結帳中最多只會套用一項品類促銷。

---

## 執行環境

- Python 3.10 以上

---

## 安裝

安裝專案：

```bash
python -m pip install .
```

若直接在專案根目錄執行，也可以不先安裝。

---

## 使用方式

### Case A

```bash
python -m shopping_cart examples/case_a.txt
```

輸出：

```text
3083.60
```

---

### Case B

```bash
python -m shopping_cart examples/case_b.txt
```

輸出：

```text
43.54
```

程式執行成功時，只會輸出**四捨五入至小數點後兩位**的最終結算金額。

若輸入格式錯誤或資料不合法，程式會顯示錯誤訊息，並回傳非零（non-zero）exit code。

---

## 執行測試

使用 Python 內建的 `unittest` 執行所有單元測試：

```bash
python -m unittest discover -s tests -v
```

Windows 使用者也可以執行驗證腳本，除了測試之外，也會進行 Python 編譯檢查：

```powershell
.\scripts\verify.ps1
```

---

## 建置

執行自動化建置：

```powershell
.\scripts\build.ps1
```

建置完成後，Wheel 套件將輸出至：

```text
dist/
```

---


## 授權

本專案僅供學習、練習及技術面試展示使用。
