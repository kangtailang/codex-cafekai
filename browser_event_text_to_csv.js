/*
 * cafekai.jp/event をChromeで開いた状態でDevTools Consoleに貼り付けて使う補助スクリプトです。
 * 表示中ページのテキストから日付・時間・タイトルらしき行をCSV化し、クリップボードへコピーします。
 * サイトのDOM構造に依存しすぎないよう、まずは表示テキストを対象にしています。
 */
(() => {
  const DEFAULT_LOCATION = window.prompt('現在表示している場所名を入力してください（例: 天神）', '天神') || '天神';
  const text = document.body.innerText.replace(/\r/g, '\n');
  const rows = [['location', 'date', 'weekday', 'time', 'title']];
  const currentYear = new Date().getFullYear();
  const eventPattern = /(\d{1,2})\/(\d{1,2})\s*[（(]([日月火水木金土])?[）)]?\s*(\d{1,2})(?::(\d{2}))?\s*[時:：][^\n「『]*[「『]?([^」』\n]+)[」』]?/g;
  let match;

  while ((match = eventPattern.exec(text)) !== null) {
    const [, month, day, weekday = '', hour, minute = '00', rawTitle] = match;
    const date = `${currentYear}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    const time = `${hour.padStart(2, '0')}:${minute}`;
    const title = rawTitle.replace(/@.+$/, '').trim();
    if (title.length > 2) {
      rows.push([DEFAULT_LOCATION, date, weekday, time, title]);
    }
  }

  const csv = rows
    .map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(','))
    .join('\n');

  navigator.clipboard.writeText(csv).then(() => {
    console.log(`CSVをクリップボードにコピーしました: ${rows.length - 1}件`);
    console.log(csv);
  }).catch(() => {
    console.log('クリップボードへのコピーに失敗しました。以下をコピーしてください。');
    console.log(csv);
  });
})();
