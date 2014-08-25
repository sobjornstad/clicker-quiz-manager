import PyRTF as rtf
import rtfunicode
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
        q = q.encode('rtfunicode')
        ca = ca.encode('rtfunicode')
        section.append(q)
        for ans in a:
            ans = ans.encode('rtfunicode')
            section.append(ans)
        section.append(ca)
        qNum += 1

    return doc

def genPreview(questions):
    """Create a plaintext preview string of the rtf file."""
    prev = []
    qNum = 1
    for question in questions:
        q, a, ca = question.getFormattedContent(qNum)
        prev.append(q)
        for ans in a:
            prev.append(ans)
        prev.append(ca + '\n')
        qNum += 1
    return '\n'.join(prev)

def render(rtfObj, f):
    DR = rtf.Renderer()
    DR.Write(rtfObj, f)
