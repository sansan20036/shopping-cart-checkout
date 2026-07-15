````markdown
# Shopping Cart Checkout

使用 Python 實作品類促銷、優惠券及購物車結算規則。

## 安裝

專案支援 Python 3.10 以上版本，核心功能沒有第三方套件依賴。

```powershell
python -m pip install .
```

若直接在專案根目錄執行，也可以不先安裝。

## 執行

執行 Case A：

```powershell
python -m shopping_cart examples/case_a.txt
```

輸出：

```text
3083.60
```

執行 Case B：

```powershell
python -m shopping_cart examples/case_b.txt
```

輸出：

```text
43.54
```

程式成功時只會輸出四捨五入至小數點後兩位的結算金額。輸入不合法時會顯示錯誤訊息，並回傳非零 exit code。

## 測試

使用 Python 標準函式庫執行所有單元測試：

```powershell
python -m unittest discover -s tests -v
```

Windows 也可以執行包含 Python 編譯檢查的自動化驗證：

```powershell
.\scripts\verify.ps1
```

## 建置

執行自動化建置：

```powershell
.\scripts\build.ps1
```

建置完成的 wheel 套件會輸出至 `dist` 目錄。

## 計算順序

1. 套用品類促銷。
2. 加總折扣後金額。
3. 套用一張有效優惠券。
4. 四捨五入至小數點後兩位。

## 題目假設

- 優惠券在到期日當天仍然有效。
- 金額等於優惠券門檻時可以使用。
- 優惠券門檻以商品促銷折扣後的總額判定。
- 同一品類在同一天最多套用一項品類促銷。
````
