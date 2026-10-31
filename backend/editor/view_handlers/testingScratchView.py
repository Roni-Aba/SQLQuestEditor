from django.shortcuts import render

from .shared import get_steps


def auswahl3(request):
    return render(
        request,
        "editor/auswahl3.html",
    )


def auswahl3v2(request):
    return render(
        request,
        "editor/auswahl3v2.html"
    )


def createlevel1agent(request):
    return render(
        request,
        "editor/createlevel1agent.html",
    )


def createlevel1agentv2(request):
    return render(
        request,
        "editor/createlevel1agentv2.html",
    )

def plugintest1(request):
    return render(
        request,
        "editor/PluginTest1.html",
    )

def plugintest2(request):
    return render(
        request, "editor/PluginTest2.html"
    )


def figma_overview_45_1891_view(request):
    return render(
        request,
        "editor/figma_overview_45_1891.html",
    )


def figma_levelauswahl_575_2535_view(request):
    return render(
        request,
        "editor/figma_levelauswahl_575_2535.html",
        {
            "steps": [
                {"number": number, "active": number == 1}
                for number in range(1, 9)
            ],
        },
    )


def createlevel1sdd(request):
    return render(
        request,
        "editor/createLevel1sdd.html",
        {
            "steps": get_steps(active_step=1),
        },
    )


def auswahlsdd(request):
    return render(request, "editor/auswahlsdd.html")


def kontakt_view(request):
    return render(request, "editor/contact.html")

def component_test_view(request):
    steps = [
        {"number": 1, "active": True},
        {"number": 2, "active": True},
        {"number": 3, "active": True},
        {"number": 4, "active": True},
        {"number": 5, "active": False},
        {"number": 6, "active": False},
        {"number": 7, "active": False},
        {"number": 8, "active": False},
    ]
    return render(request, "editor/test.html", {
        "steps": steps,
    })