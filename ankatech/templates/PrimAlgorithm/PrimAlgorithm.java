import java.util.*;

class PrimAlgorithm {

    // Prim algoritmasÃ„Â± ile Minimum Spanning Tree (MST) oluÃ…Å¸turma fonksiyonu
    void primMST(int[][] graph, int V) {
        int[] parent = new int[V]; // MST'nin bir parÃƒÂ§asÃ„Â± olan dÃƒÂ¼Ã„Å¸ÃƒÂ¼mleri saklar
        int[] key = new int[V];    // Minimum aÃ„Å¸Ã„Â±rlÃ„Â±k deÃ„Å¸erlerini saklar
        boolean[] mstSet = new boolean[V]; // MST'ye dahil edilen dÃƒÂ¼Ã„Å¸ÃƒÂ¼mleri takip eder

        // TÃƒÂ¼m dÃƒÂ¼Ã„Å¸ÃƒÂ¼mler iÃƒÂ§in anahtar deÃ„Å¸erlerini sonsuz olarak baÃ…Å¸lat
        Arrays.fill(key, Integer.MAX_VALUE);
        key[0] = 0; // Ã„Â°lk dÃƒÂ¼Ã„Å¸ÃƒÂ¼mÃƒÂ¼n anahtarÃ„Â±nÃ„Â± 0 yap
        parent[0] = -1; // Ã„Â°lk dÃƒÂ¼Ã„Å¸ÃƒÂ¼mÃƒÂ¼n bir ebeveyni yok

        for (int count = 0; count < V - 1; count++) {
            // MST'ye dahil edilmeyen dÃƒÂ¼Ã„Å¸ÃƒÂ¼mlerden minimum anahtar deÃ„Å¸ere sahip olanÃ„Â± seÃƒÂ§
            int u = minKey(key, mstSet, V);

            // SeÃƒÂ§ilen dÃƒÂ¼Ã„Å¸ÃƒÂ¼mÃƒÂ¼ MST'ye dahil et
            mstSet[u] = true;

            // SeÃƒÂ§ilen dÃƒÂ¼Ã„Å¸ÃƒÂ¼me komÃ…Å¸u olan dÃƒÂ¼Ã„Å¸ÃƒÂ¼mleri gÃƒÂ¼ncelle
            for (int v = 0; v < V; v++) {
                // EÃ„Å¸er graph[u][v] bir kenarsa ve v MST'ye dahil edilmemiÃ…Å¸se
                // ve graph[u][v] anahtar deÃ„Å¸erinden kÃƒÂ¼ÃƒÂ§ÃƒÂ¼kse
                if (graph[u][v] != 0 && !mstSet[v] && graph[u][v] < key[v]) {
                    parent[v] = u;
                    key[v] = graph[u][v];
                }
            }
        }

        // OluÃ…Å¸an MST'yi yazdÃ„Â±r
        printMST(parent, graph, V);
    }

    // MST'ye dahil edilmeyen dÃƒÂ¼Ã„Å¸ÃƒÂ¼mler arasÃ„Â±ndan minimum anahtar deÃ„Å¸ere sahip olanÃ„Â± bulur
    int minKey(int[] key, boolean[] mstSet, int V) {
        int min = Integer.MAX_VALUE, minIndex = -1;

        for (int v = 0; v < V; v++) {
            if (!mstSet[v] && key[v] < min) {
                min = key[v];
                minIndex = v;
            }
        }

        return minIndex;
    }

    // MST'yi yazdÃ„Â±ran fonksiyon
    void printMST(int[] parent, int[][] graph, int V) {
        System.out.println("Minimum Spanning Tree'deki Kenarlar");
        int minimumCost = 0;
        for (int i = 1; i < V; i++) {
            System.out.println(parent[i] + " -- " + i + " == " + graph[i][parent[i]]);
            minimumCost += graph[i][parent[i]];
        }
        System.out.println("Minimum Spanning Tree'nin Toplam Maliyeti: " + minimumCost);
    }
    public static void main(String[] args) {
        int V = 5; // DÃƒÂ¼Ã„Å¸ÃƒÂ¼m sayÃ„Â±sÃ„Â±
        int[][] graph = {
                {0, 2, 0, 6, 0},
                {2, 0, 3, 8, 5},
                {0, 3, 0, 0, 7},
                {6, 8, 0, 0, 9},
                {0, 5, 7, 9, 0}
        };
        PrimAlgorithm prim = new PrimAlgorithm();
        prim.primMST(graph, V);
    }
}