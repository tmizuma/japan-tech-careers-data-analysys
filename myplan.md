# ゴール

company_list.csv でリンク切れの logo url を正しい URL に置き換える

# 手段

company_logo URL はほとんどの URL が無効です。おそらく logo.clearbit.com の問題なので、logo.clearbit.com を使わないようにしたいです。
具体的には、company_url にアクセスし、ogp で logo が取得できる可能性があるためこれで置き換えたいと思います。

新たに、company_logo.csv を追加し、結果を一時保存してください
ヘッダ: company_id (mercari 等) / 取得した compaly_logo_url / resut (OK/NG) / reason
logo の URL が見つかった場合、OK, NG の場合は reason に理由やメモを書いてください。全ての企業に対して、この作業を行い、company_logo.csv を完成させてください。それ以外のファイルは編集しないでください。
