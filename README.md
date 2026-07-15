# Shopping Cart Checkout

使用 Python 實作品類促銷、優惠券及購物車結算規則。

## 安裝

專案支援 Python 3.10 以上版本，核心功能沒有第三方套件依賴。

```powershell
python -m pip install .
```

## 執行

讀取輸入檔案：

```powershell
python -m shopping_cart examples/case_a.txt
```

也可以透過標準輸入執行：

```powershell
Get-Content examples/case_b.txt | python -m shopping_cart
```

## 測試

```powershell
python -m unittest discover -s tests -v
```

Windows 也可以執行包含編譯檢查的自動化驗證：

```powershell
.\scripts\verify.ps1
```

## 建置

```powershell
.\scripts\build.ps1
```

建置完成的 wheel 套件會輸出至 `dist`。

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
