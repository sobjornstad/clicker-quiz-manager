import PyRTF as rtf
from questions import Question

def genRtfFile(questions):
    doc = rtf.Document()
    section = rtf.Section()
    doc.Sections.append(section)

    section.append("MULTIPLE CHOICE")
    section.append("")
    qNum = 1
    for question in questions:
        q, a, ca = question.getFormattedContent(qNum)
        section.append(q)
        for ans in a:
            section.append(ans)
        section.append(ca)
        qNum += 1

    return doc

def render(questions, filename):
    DR = rtf.Renderer()
    doc3 = genRtfFile(questions)
    DR.Write(doc3, file(filename, 'w'))
