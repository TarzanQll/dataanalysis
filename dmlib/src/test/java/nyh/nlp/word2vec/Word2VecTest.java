package nyh.nlp.word2vec;

/**
 * \* Created with IntelliJ IDEA.
 * \* User: nyh
 * \* Date: 17-11-29
 * \* Time: 下午6:08
 * \* Description:
 * \
 */
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.List;

import org.ansj.domain.Term;
import org.ansj.splitWord.analysis.ToAnalysis;

import com.alibaba.fastjson.JSONObject;
import nyh.nlp.word2vec.Learn;
import nyh.nlp.word2vec.Word2VEC;

import love.cq.util.IOUtil;
import love.cq.util.StringUtil;

public class Word2VecTest {
    private static final File sportCorpusFile =
            new File("dmlib/data/word2vec/swresult_withoutnature.txt");

    public static void main(String[] args) throws IOException {
        File[] files = new File("dmlib/data/word2vec").listFiles();

        //构建语料
        FileOutputStream fos = new FileOutputStream(sportCorpusFile);
        for (File file : files) {
            if (file.canRead() && file.getName().endsWith(".txt")) {
                parserFile(fos, file);
            }
        }

        //进行分词训练

        Learn lean = new Learn() ;

        lean.learnFile(sportCorpusFile) ;

        lean.saveModel(new File("dmlib/model/vector.mod")) ;



        //加载测试

        Word2VEC w2v = new Word2VEC() ;

        w2v.loadJavaModel("dmlib/model/vector.mod") ;

        System.out.println(w2v.distance("毛泽东")); ;

    }

    private static void parserFile(FileOutputStream fos, File file) throws FileNotFoundException,
            IOException {
        // TODO Auto-generated method stub
        BufferedReader br = IOUtil.getReader(file.getAbsolutePath(), IOUtil.UTF8);
        String temp = null;
        JSONObject parse = null;
        while ((temp = br.readLine()) != null) {
            parse = JSONObject.parseObject(temp);
            paserStr(fos, parse.getString("title"));
            paserStr(fos, StringUtil.rmHtmlTag(parse.getString("content")));
        }
    }

    private static void paserStr(FileOutputStream fos, String title) throws IOException {
        List<Term> parse2 = ToAnalysis.parse(title) ;
        StringBuilder sb = new StringBuilder() ;
        for (Term term : parse2) {
            sb.append(term.getName()) ;
            sb.append(" ");
        }
        fos.write(sb.toString().getBytes()) ;
        fos.write("\n".getBytes()) ;
    }
}