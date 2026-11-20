package net.semtle.ninja;
import android.app.Activity;
import android.content.*;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.speech.tts.TextToSpeech;
import java.io.*;
import java.nio.*;
import java.util.Locale;
public final class NinjaPlatform {
    private static TextToSpeech tts;
    private static volatile boolean ready;
    public static void configure(Activity a) {
        a.runOnUiThread(()->{
            // This canvas-only game uses hardware keys, never an on-screen text editor.
            a.getWindow().setFlags(android.view.WindowManager.LayoutParams.FLAG_ALT_FOCUSABLE_IM, android.view.WindowManager.LayoutParams.FLAG_ALT_FOCUSABLE_IM);
            a.getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN | android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_NOTHING);
            android.view.View view=a.getWindow().getDecorView();
            android.view.inputmethod.InputMethodManager ime=(android.view.inputmethod.InputMethodManager)a.getSystemService(Context.INPUT_METHOD_SERVICE);
            if(ime!=null) ime.hideSoftInputFromWindow(view.getWindowToken(),0);
        });
    }
    public static synchronized int ready(Activity a) {
        if(tts==null) a.runOnUiThread(()->{
            if(tts!=null) return;
            tts=new TextToSpeech(a.getApplicationContext(),status->{
                ready=status==TextToSpeech.SUCCESS && tts.setLanguage(Locale.KOREA)>=TextToSpeech.LANG_AVAILABLE;
            });
        });
        return ready?1:0;
    }
    public static int speak(Activity a,byte[] bytes,float rate,float pitch,float volume,boolean interrupt) {
        if(ready(a)==0) return 0;
        String text=new String(bytes,java.nio.charset.StandardCharsets.UTF_8);
        a.runOnUiThread(()->{
            android.os.Bundle params=new android.os.Bundle();
            params.putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME,volume);
            tts.setSpeechRate(rate); tts.setPitch(pitch);
            tts.speak(text,interrupt?TextToSpeech.QUEUE_FLUSH:TextToSpeech.QUEUE_ADD,params,"ninja-"+System.nanoTime());
        }); return 1;
    }
    public static void stop(Activity a) { a.runOnUiThread(()->{if(tts!=null) tts.stop();}); }
    public static int result(Activity a,byte[] bytes,int w,int h,byte[] caption,boolean save) {
        if(w<1||h<1||bytes.length!=w*h*4) return 0;
        a.runOnUiThread(()->{
            try {
                int[] pixels=new int[w*h]; ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).asIntBuffer().get(pixels);
                for(int i=0;i<pixels.length;i++) pixels[i]|=0xff000000;
                Bitmap bitmap=Bitmap.createBitmap(pixels,w,h,Bitmap.Config.ARGB_8888);
                File dir=new File(a.getCacheDir(),"ninja-results"); dir.mkdirs();
                File file=new File(dir,"중급닌자시험-결과.png");
                try(OutputStream out=new FileOutputStream(file)) { bitmap.compress(Bitmap.CompressFormat.PNG,100,out); }
                bitmap.recycle();
                Uri uri=new Uri.Builder().scheme("content").authority(a.getPackageName()+".ninja.results").appendPath(file.getName()).build();
                Intent intent=new Intent(Intent.ACTION_SEND).setType("image/png").putExtra(Intent.EXTRA_STREAM,uri)
                    .putExtra(Intent.EXTRA_TEXT,new String(caption,java.nio.charset.StandardCharsets.UTF_8)).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                a.startActivity(Intent.createChooser(intent,save?"결과 이미지 저장":"결과 공유하기"));
            } catch(Exception e) { android.util.Log.e("NinjaTest","result export",e); }
        }); return 1;
    }
    public static final class ResultsProvider extends ContentProvider {
        public boolean onCreate(){return true;}
        private File file(Uri uri)throws FileNotFoundException {
            String name=uri.getLastPathSegment();
            if(name==null||name.contains("/")||name.contains(".."))throw new FileNotFoundException();
            return new File(new File(getContext().getCacheDir(),"ninja-results"),name);
        }
        public ParcelFileDescriptor openFile(Uri uri,String mode)throws FileNotFoundException {
            if(!"r".equals(mode))throw new FileNotFoundException();
            return ParcelFileDescriptor.open(file(uri),ParcelFileDescriptor.MODE_READ_ONLY);
        }
        public String getType(Uri uri){return "image/png";}
        public Cursor query(Uri uri,String[] projection,String selection,String[] args,String sort){
            try {File f=file(uri);MatrixCursor c=new MatrixCursor(new String[]{"_display_name","_size"});c.addRow(new Object[]{f.getName(),f.length()});return c;}catch(Exception e){return null;}
        }
        public Uri insert(Uri u,ContentValues v){return null;}
        public int delete(Uri u,String s,String[] a){return 0;}
        public int update(Uri u,ContentValues v,String s,String[] a){return 0;}
    }
}
