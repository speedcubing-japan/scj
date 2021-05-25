import app.consts


def context_processor(req):
    return {
        'consts': app.consts
    }