from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import YouTubeURLForm, QualitySelectionForm
from pytube import YouTube
import io

def index(request):
    if request.method == 'POST':
        form = YouTubeURLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            yt = YouTube(url)
            request.session['video_url'] = url

            # get all available video and audio streams
            video_streams = yt.streams.filter(progressive=True)
            audio_streams = yt.streams.filter(only_audio=True)
            choices = [(stream.itag, f'{stream.mime_type} {stream.resolution or stream.abr}') for stream in video_streams] + \
                      [(stream.itag, f'{stream.mime_type} {stream.abr}') for stream in audio_streams]

            request.session['choices'] = choices
            request.session['title'] = yt.title
            request.session['thumbnail_url'] = yt.thumbnail_url

            return redirect('download')
    else:
        form = YouTubeURLForm()

    return render(request, 'yt_downloader/index.html', {'form': form})

def download(request):
    '''function to handle file downloads'''
    if 'choices' not in request.session:
        return redirect('index')
    
    if request.method == 'POST':
        itag = request.POST.get('itag')
        if itag:
            url = request.session['video_url']
            yt = YouTube(url)
            stream = yt.streams.get_by_itag(itag)

            # Create a stream buffer
            buffer = io.BytesIO()
            stream.stream_to_buffer(buffer)
            buffer.seek(0)

            # Prepare the response
            response = HttpResponse(buffer, content_type=stream.mime_type)
            response['Content-Disposition'] = f'attachment; filename="{yt.title}.{stream.subtype}"'
            return response

    # Prepare data for rendering
    choices = request.session['choices']
    thumbnail_url = request.session['thumbnail_url']
    title = request.session['title']
    
    context = {
        'choices': choices,
        'thumbnail_url': thumbnail_url,
        'title': title,
    }

    return render(request, 'yt_downloader/download.html', context)


""" def download(request):
    if 'choices' not in request.session:
        return redirect('index')

    if request.method == 'POST':
        form = QualitySelectionForm(request.POST)
        form.fields['quality'].choices = request.session['choices']
        if form.is_valid():
            itag = form.cleaned_data['quality']
            url = request.session['video_url']
            yt = YouTube(url)
            stream = yt.streams.get_by_itag(itag)

            # Create a stream buffer
            buffer = io.BytesIO()
            stream.stream_to_buffer(buffer)
            buffer.seek(0)

            # Prepare the response
            response = HttpResponse(buffer, content_type=stream.mime_type)
            response['Content-Disposition'] = f'attachment; filename="{yt.title}.{stream.subtype}"'
            return response
    else:
        form = QualitySelectionForm()
        form.fields['quality'].choices = request.session['choices']

    return render(request, 'yt_downloader/download.html', {'form': form})
 """
