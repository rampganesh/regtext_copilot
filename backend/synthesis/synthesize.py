from llm import llm


def synthesize(question, passages):
    parts = []
    for i, p in enumerate(passages):
        parts.append('[source %s] %s: %s' % (i + 1, p['title'], p['content']))
    context = chr(10).join(parts)
    prompt = (
        'You are assisting a regulatory reporting analyst. '
        'Answer using only the sources below, phrased as evidence not certainty. '
        'Begin your answer with the exact words:\n The relevant sources indicate\n'
        'Never state that a provision is the applicable requirement. '
        'If the sources do not support an answer, say the evidence is insufficient.\n\n'
        'Sources:\n' + context + '\n\n'
        'Question: ' + question
    )
    messages = [{'role': 'user', 'content': prompt}]
    return llm.chat(messages)
