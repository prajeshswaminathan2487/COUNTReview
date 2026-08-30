const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

const INK = "1C2530";
const MUTED = "6B7684";
const BORDER = "D9DDE2";
const BG = "F4F5F6";

const PURPLE = "6C5CE7";
const BLUE = "2F8FE0";
const GREEN = "1FA971";
const GOLD = "D89B00";
const PINK = "E0186F";

const BAND_GREEN_BG = "DCF3E6";
const BAND_BLUE_BG = "DCEBF9";
const BAND_YELLOW_BG = "F6EFC9";
const BAND_RED_BG = "F8DCE1";

const s = pres.addSlide();
s.background = { color: BG };

/* ---------- Header ---------- */
s.addText("C.O.U.N.T. Review — {{REVIEW_DATE}}", {
  x: 0.3, y: 0.22, w: 9.5, h: 0.5,
  fontSize: 24, bold: true, color: INK, fontFace: "Arial",
});

s.addText("{{SUBHEADER}}", {
  x: 0.3, y: 0.68, w: 8, h: 0.3,
  fontSize: 12, color: MUTED, fontFace: "Arial",
});

s.addShape("roundRect", {
  x: 10.85, y: 0.2, w: 2.2, h: 0.5, rectRadius: 0.05,
  fill: { color: "E4E7EA" }, line: { color: BORDER, width: 1 },
});
s.addText("REACH {{TOTAL_SCORE}}/25", {
  x: 10.85, y: 0.2, w: 2.2, h: 0.5,
  fontSize: 13, bold: true, color: INK, align: "center", valign: "middle", fontFace: "Arial",
});

/* ---------- Account Snapshot bar ---------- */
s.addShape("rect", {
  x: 0.3, y: 1.02, w: 12.73, h: 0.36,
  fill: { color: "FFFFFF" }, line: { color: BORDER, width: 1 },
});
s.addText([
  { text: "ACCOUNT SNAPSHOT", options: { bold: true, color: INK } },
  { text: "  |  {{ACCOUNT_SNAPSHOT}}", options: { color: MUTED } },
], {
  x: 0.5, y: 1.02, w: 12.4, h: 0.36,
  fontSize: 10.5, valign: "middle", fontFace: "Arial",
});

/* ---------- COUNT header row (static labels, no dynamic content) ---------- */
const countLabels = ["Corporate & Contracts", "Opportunity", "Update (Value Add)", "Number (Targets)", "Tenure & Team"];
const colGap = 0.15;
const colWidth = (12.73 - 4 * colGap) / 5;
const colX = [0, 1, 2, 3, 4].map((i) => 0.3 + i * (colWidth + colGap));

const countY = 1.58;
const countH = 0.55;

countLabels.forEach((label, i) => {
  s.addShape("rect", {
    x: colX[i], y: countY, w: colWidth, h: countH,
    fill: { color: "FFFFFF" }, line: { color: BORDER, width: 1 },
  });
  s.addText(label, {
    x: colX[i] + 0.12, y: countY, w: colWidth - 0.24, h: countH,
    fontSize: 11, bold: true, color: INK, valign: "middle", fontFace: "Arial",
  });
});

/* ---------- REACH cards row ---------- */
// Titles are FIXED (never AI-generated) so the framework's meaning never drifts.
// Only score + evidence are placeholder tokens.
const reachData = [
  { letter: "R", color: PURPLE, title: "Return on Assets", scoreToken: "{{R_SCORE}}", evidenceToken: "{{R_EVIDENCE}}" },
  { letter: "E", color: BLUE, title: "SI Value to Customer", scoreToken: "{{E_SCORE}}", evidenceToken: "{{E_EVIDENCE}}" },
  { letter: "A", color: GREEN, title: "AR & Contracts", scoreToken: "{{A_SCORE}}", evidenceToken: "{{A_EVIDENCE}}" },
  { letter: "C", color: GOLD, title: "Customer Stage & Crisis", scoreToken: "{{C_SCORE}}", evidenceToken: "{{C_EVIDENCE}}" },
  { letter: "H", color: PINK, title: "High Performers", scoreToken: "{{H_SCORE}}", evidenceToken: "{{H_EVIDENCE}}" },
];

const barY = 2.28;
const barH = 0.05;
const cardY = 2.33;
const cardH = 2.55;

reachData.forEach((d, i) => {
  s.addShape("rect", {
    x: colX[i], y: barY, w: colWidth, h: barH,
    fill: { color: d.color }, line: { type: "none" },
  });

  s.addShape("roundRect", {
    x: colX[i], y: cardY, w: colWidth, h: cardH, rectRadius: 0.06,
    fill: { color: "FFFFFF" }, line: { color: BORDER, width: 1 },
  });

  s.addText(d.letter, {
    x: colX[i] + 0.15, y: cardY + 0.15, w: colWidth - 0.3, h: 0.45,
    fontSize: 26, bold: true, color: d.color, fontFace: "Georgia",
  });

  s.addText(d.title, {
    x: colX[i] + 0.15, y: cardY + 0.62, w: colWidth - 0.3, h: 0.4,
    fontSize: 12, bold: true, color: INK, fontFace: "Arial",
  });

  s.addText("SCORE " + d.scoreToken, {
    x: colX[i] + 0.15, y: cardY + 1.02, w: colWidth - 0.3, h: 0.3,
    fontSize: 12, bold: true, color: d.color, fontFace: "Arial",
  });

  s.addText(d.evidenceToken, {
    x: colX[i] + 0.15, y: cardY + 1.35, w: colWidth - 0.3, h: cardH - 1.45,
    fontSize: 10, color: INK, fontFace: "Arial", valign: "top",
  });
});

/* ---------- REACH Scorecard row ---------- */
const scoreY = 5.08;
const scoreH = 0.72;

const labelW = 1.95;
s.addShape("rect", {
  x: 0.3, y: scoreY, w: labelW, h: scoreH,
  fill: { color: "FFFFFF" }, line: { color: BORDER, width: 1 },
});
s.addText("REACH\nSCORECARD", {
  x: 0.45, y: scoreY + 0.05, w: labelW - 0.3, h: 0.32,
  fontSize: 10, bold: true, color: INK, fontFace: "Arial", lineSpacingMultiple: 0.95,
});
s.addText("{{TOTAL_SCORE}} / 25", {
  x: 0.45, y: scoreY + 0.36, w: labelW - 0.3, h: 0.28,
  fontSize: 12.5, bold: true, color: INK, fontFace: "Arial",
});
s.addText("{{CLASSIFICATION}}", {
  x: 0.45, y: scoreY + 0.58, w: labelW - 0.3, h: 0.2,
  fontSize: 9, italic: true, color: MUTED, fontFace: "Arial",
});

const bands = [
  { range: "21-25", label: "High Performer", bg: BAND_GREEN_BG },
  { range: "16-20", label: "Healthy Growth", bg: BAND_BLUE_BG },
  { range: "11-15", label: "Needs Attention", bg: BAND_YELLOW_BG },
  { range: "5-10", label: "At Risk", bg: BAND_RED_BG },
];

const bandGap = 0.15;
const bandStartX = 0.3 + labelW + bandGap;
const bandTotalW = 12.73 - labelW - bandGap;
const bandW = (bandTotalW - 3 * bandGap) / 4;

bands.forEach((b, i) => {
  const x = bandStartX + i * (bandW + bandGap);
  s.addShape("roundRect", {
    x, y: scoreY, w: bandW, h: scoreH, rectRadius: 0.08,
    fill: { color: b.bg }, line: { type: "none" },
  });
  s.addText(b.range, {
    x, y: scoreY + 0.1, w: bandW, h: 0.3,
    fontSize: 11, color: INK, align: "center", fontFace: "Arial",
  });
  s.addText(b.label, {
    x, y: scoreY + 0.38, w: bandW, h: 0.3,
    fontSize: 11, color: INK, align: "center", fontFace: "Arial",
  });
});

pres.writeFile({ fileName: "/home/claude/count-automation/assets/count_template.pptx" }).then(() => {
  console.log("done");
});
