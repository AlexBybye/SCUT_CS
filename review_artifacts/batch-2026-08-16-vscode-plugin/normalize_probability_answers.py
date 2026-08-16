from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "review_artifacts/batch-2026-08-16-vscode-plugin/input"
OUTPUT = ROOT / "knowledge/probability"


def clean_line(line: str, source_id: str, image_dir: str) -> str:
    line = line.replace("\u00a0", " ").rstrip()
    if line.startswith("- "):
        line = line[2:]
    line = line.replace("**", "")
    image_pattern = rf"!\[\]\(images/{re.escape(image_dir)}/image_(\d{{3}})\.x-wmf\)"
    line = re.sub(
        image_pattern,
        lambda match: f"![](assets/{source_id}/image-{match.group(1)}.png)",
        line,
    )
    return line


def compact(lines: list[str]) -> list[str]:
    result: list[str] = []
    for line in lines:
        if not line and result and not result[-1]:
            continue
        result.append(line)
    while result and not result[-1]:
        result.pop()
    return result


def add_question(
    output: list[str], number: int, heading: str, remainder: str = ""
) -> None:
    if output and output[-1]:
        output.append("")
    output.extend([f"<!-- question: {number} -->", "", f"## {heading}", ""])
    if remainder:
        output.append(remainder)


def normalize_2014() -> None:
    source_id = "probability-theory-004"
    title = "2014春《概率论与数理统计》A卷答案"
    raw = (INPUT / "probability__2014春A卷答案.md").read_text(encoding="utf-8")
    body = [clean_line(line, source_id, "probability_2014a_133418") for line in raw.splitlines()[22:]]

    output = [
        "---",
        f"source_id: {source_id}",
        "course_id: probability_theory",
        f"title: {title}",
        "original_file: 学科资料/概率论/往年卷/2014春A卷答案.docx",
        "document_role: past_exam_answer",
        "year: 2014",
        "locator_type: heading",
        "---",
        "",
        f"# {title}",
        "",
        "诚信应考，考试作弊将带来严重后果！",
        "",
        "华南理工大学本科生期末考试",
        "",
        "《概率论与数理统计》A卷",
        "",
        "**注意事项：**",
        "",
        "1. 开考前请将密封线内各项信息填写清楚；",
        "2. 所有答案请直接答在试卷上；",
        "3. 考试形式：闭卷；",
        "4. 本试卷共八大题，满分100分，考试时间120分钟。",
        "",
        "| 题号 | 一 | 二 | 三 | 四 | 五 | 六 | 七 | 八 | 总分 |",
        "|---|---|---|---|---|---|---|---|---|---|",
        "| 得分 |  |  |  |  |  |  |  |  |  |",
        "",
        "**注意：** ![](assets/probability-theory-004/image-013.png)",
        "",
        "![](assets/probability-theory-004/image-014.png)",
        "",
        "![](assets/probability-theory-004/image-015.png)",
    ]

    headings = {
        "一、（12分）": (1, "一、（12分）"),
        "二、（10分）": (2, "二、（10分）"),
        "三、 (10分)": (3, "三、（10分）"),
        "四、(15分)": (4, "四、（15分）"),
        "五、（12）": (5, "五、（12分）"),
        "六、（10分）": (6, "六、（10分）"),
        "七、（10分）": (7, "七、（10分）"),
        "八、（21分）": (8, "八、（21分）"),
    }

    for line in body:
        matched = False
        for prefix, (number, heading) in headings.items():
            if line.startswith(prefix):
                remainder = line[len(prefix) :].lstrip("、，, ")
                add_question(output, number, heading, remainder)
                matched = True
                break
        if matched:
            continue
        if line.startswith("32 ，1.55"):
            line = "1.32　1.55　1.36　1.40　1.44"
        output.append(line)

    # The plugin reduced the source coordinate diagram to a one-column pseudo-table.
    table_start = output.index("| *x* |")
    table_end = output.index("| 2 |", table_start)
    output[table_start : table_end + 1] = [
        "![](assets/probability-theory-004/diagram-001.png)"
    ]

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / f"{source_id}.md").write_text(
        "\n".join(compact(output)) + "\n", encoding="utf-8"
    )


def normalize_2016() -> None:
    source_id = "probability-theory-006"
    title = "2016春季《概率论与数理统计》A卷答案"
    raw = (INPUT / "probability__2016春季A卷答案.md").read_text(encoding="utf-8")
    body = [clean_line(line, source_id, "probability_2016a_133615") for line in raw.splitlines()]

    output = [
        "---",
        f"source_id: {source_id}",
        "course_id: probability_theory",
        f"title: {title}",
        "original_file: 学科资料/概率论/往年卷/2016春季A卷答案.docx",
        "document_role: past_exam_answer",
        "year: 2016",
        "locator_type: heading",
        "---",
        "",
        f"# {title}",
    ]

    headings = {
        "一、 填空题（每小题3分，共18分）": (1, "一、填空题（每小题3分，共18分）"),
        "二、单项选择题（每小题3分，共18分）": (2, "二、单项选择题（每小题3分，共18分）"),
        "三、(10分）": (3, "三、（10分）"),
        "四、（8分）": (4, "四、（8分）"),
        "五.（12分）": (5, "五、（12分）"),
        "六．（8分）": (6, "六、（8分）"),
        "七、(16分)": (7, "七、（16分）"),
        "八．（10分）": (8, "八、（10分）"),
    }
    q2 = False

    for line in body:
        matched = False
        for prefix, (number, heading) in headings.items():
            if line.startswith(prefix):
                remainder = line[len(prefix) :].lstrip("、，, ")
                add_question(output, number, heading, remainder)
                q2 = number == 2
                matched = True
                break
        if matched:
            continue

        if q2 and line.startswith("设![](assets/probability-theory-006/image-090.png)"):
            line = "4．" + line
        elif q2 and line.startswith("随机变量![](assets/probability-theory-006/image-103.png)"):
            line = "5．" + line
        elif q2 and line.startswith("某人向同一目标独立重复射击"):
            line = "6．" + line

        if "的联合概率分布|" in line:
            before, table = line.split("的联合概率分布|", 1)
            output.extend(
                [
                    before + "的联合概率分布：",
                    "",
                    "|" + table,
                    "|---|---:|---:|---:|---:|",
                ]
            )
            continue

        if line.startswith("7 100.5 101.2"):
            line = "98.7　100.5　101.2　98.3　99.7　99.5　101.4　100.5"
        output.append(line)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / f"{source_id}.md").write_text(
        "\n".join(compact(output)) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    normalize_2014()
    normalize_2016()
