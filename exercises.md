# K4 — Ngày 1: Bài Tập & Phản Ánh
## Khám Phá LLM API | Phiếu Thực Hành

**Thời lượng:** 4 tiếng
**Cách làm:** Trả lời từng câu ngay sau khi hoàn thành block tương ứng —
đừng để dồn hết về cuối buổi. Thay dòng `*Câu trả lời của bạn*` bằng câu
trả lời thật (chấm tự động sẽ đếm số câu đã trả lời).

---

## Block 1 — API Cơ Bản (trả lời sau Checkpoint 1)

### Câu 1.1 — Độ nhạy của temperature
Gọi `call_openai` với temperature 0.0, 0.5, 1.0 và 1.5 dùng prompt
**"Hãy kể cho tôi một sự thật thú vị về Việt Nam."**

**Bạn nhận thấy quy luật gì qua bốn phản hồi?** (2–3 câu)
> Khi temperature thấp, phản hồi thường ổn định, đi thẳng vào sự thật chính và ít thay đổi giữa các lần gọi. Khi temperature tăng lên 1.0 hoặc 1.5, câu trả lời có xu hướng đa dạng hơn về cách diễn đạt và ví dụ, nhưng cũng dễ dài dòng hoặc kém chắc chắn hơn.

### Câu 1.2 — Chọn temperature cho sản phẩm
**Bạn sẽ đặt temperature bao nhiêu cho chatbot hỗ trợ khách hàng, và tại sao?**
> Tôi sẽ đặt khoảng 0.2 đến 0.4. Chatbot hỗ trợ khách hàng cần ưu tiên câu trả lời nhất quán, đúng quy trình và ít sáng tạo quá mức; vẫn có một chút linh hoạt để diễn đạt tự nhiên theo tình huống của người dùng.

### Câu 1.3 — Đánh đổi chi phí
Kịch bản: 10.000 người dùng hoạt động mỗi ngày, mỗi người gọi API 3 lần,
mỗi lần trung bình ~350 token đầu ra.

**Ước tính GPT-4o đắt hơn GPT-4o-mini bao nhiêu lần cho workload này? Nêu một
trường hợp GPT-4o xứng đáng với chi phí và một trường hợp nên dùng mini:**
> Với giá output trong `PRICING_PER_1K_TOKENS`, GPT-4o là 0.010 USD/1K token còn GPT-4o-mini là 0.0006 USD/1K token, tức GPT-4o đắt hơn khoảng 16.7 lần cho cùng lượng output. GPT-4o xứng đáng khi tác vụ cần suy luận khó, độ chính xác cao hoặc trả lời nội dung nhạy cảm quan trọng; mini phù hợp cho FAQ, phân loại đơn giản, tóm tắt ngắn hoặc các lượt chat số lượng lớn cần tối ưu chi phí.

---

## Block 2 — System Prompt & Token (trả lời sau Checkpoint 2)

### Câu 2.1 — Sức mạnh của persona
Gọi `chat_with_system_prompt` hai lần với cùng câu hỏi
**"Giải thích blockchain là gì?"** nhưng hai system prompt khác nhau:
- "Bạn là giáo viên tiểu học, giải thích thật đơn giản cho trẻ 8 tuổi."
- "Bạn là chuyên gia tài chính, trả lời chuyên sâu bằng thuật ngữ kỹ thuật."

**Hai phản hồi khác nhau như thế nào (độ dài, từ vựng, ví dụ)? System prompt
ảnh hưởng đến hành vi model ra sao?** (3–4 câu)
> Với persona giáo viên tiểu học, câu trả lời thường ngắn hơn, dùng từ đơn giản và ví dụ đời thường như cuốn sổ ghi chép chung. Với persona chuyên gia tài chính, phản hồi có nhiều thuật ngữ hơn như sổ cái phân tán, đồng thuận, giao dịch, bảo mật và ứng dụng trong tài sản số. System prompt giống phần định vai: nó không đổi câu hỏi của người dùng, nhưng đổi cách model chọn giọng văn, mức chi tiết và loại ví dụ.

### Câu 2.2 — tiktoken vs đếm từ
Chọn một đoạn văn tiếng Việt ~100 từ. So sánh số token theo `count_tokens`
(tiktoken) với ước lượng `số từ / 0.75` mà Part 1 đã dùng.

**Hai con số chênh nhau bao nhiêu phần trăm? Vì sao tiếng Việt thường tốn
nhiều token hơn tiếng Anh cùng độ dài?**
> Số token theo `tiktoken` thường cao hơn ước lượng thô `số từ / 0.75`, nhất là với câu tiếng Việt có dấu; mức chênh có thể vào khoảng vài chục phần trăm tùy đoạn văn. Tiếng Việt thường tốn nhiều token hơn vì tokenizer có thể tách dấu thanh, âm tiết và các từ ít gặp thành nhiều mảnh nhỏ, trong khi nhiều từ tiếng Anh phổ biến đã có token gọn hơn.

---

## Block 3 — Streaming & Độ Bền (trả lời sau Checkpoint 3)

### Câu 3.1 — Trải nghiệm người dùng với streaming
**Streaming quan trọng nhất trong trường hợp nào, và khi nào thì
non-streaming lại phù hợp hơn?** (1 đoạn văn)
> Streaming quan trọng nhất khi câu trả lời dài hoặc người dùng đang tương tác trực tiếp với chatbot, vì ký tự đầu tiên xuất hiện sớm làm cảm giác chờ đỡ khó chịu hơn dù tổng thời gian sinh câu trả lời không giảm nhiều. Nó phù hợp cho trợ lý viết bài, giải thích dài, hoặc chat nhiều lượt. Non-streaming lại hợp hơn khi cần xử lý kết quả trọn gói, ví dụ gọi API phía backend để phân loại, chấm điểm, lưu JSON, hoặc khi giao diện chỉ cần hiện kết quả sau cùng.

### Câu 3.2 — Vì sao backoff theo cấp số nhân?
**So với delay cố định (ví dụ luôn chờ 1 giây), exponential backoff có lợi
thế gì khi API bị quá tải? Điều gì xảy ra nếu hàng nghìn client cùng retry
với delay cố định giống nhau?**
> Exponential backoff giúp giảm áp lực lên API bằng cách giãn dần khoảng cách giữa các lần thử lại, cho server thêm thời gian hồi phục sau lỗi tạm thời hoặc quá tải. Nếu hàng nghìn client đều retry với delay cố định giống nhau, chúng có thể cùng bắn request lại đúng một thời điểm, tạo thêm một đợt quá tải mới. Trong hệ thống thật thường thêm jitter ngẫu nhiên để các lượt retry không bị đồng bộ với nhau.

---

## Block 4 — Mini-Project (trả lời sau Checkpoint 4)

### Câu 4.1 — Thiết kế persona
**Bạn chọn persona gì cho trợ lý của mình? Viết lại system prompt đó và giải
thích 1–2 lựa chọn từ ngữ quan trọng trong prompt (ví dụ: vì sao yêu cầu
"trả lời ngắn gọn", vì sao chỉ định ngôn ngữ...):**
> Tôi chọn persona: "Bạn là trợ giảng thân thiện của khóa AI, trả lời bằng tiếng Việt rõ ràng, ngắn gọn và ưu tiên ví dụ thực hành." Tôi yêu cầu "trả lời bằng tiếng Việt" để phù hợp người học trong lớp, và "ngắn gọn" để chatbot không làm người mới bị ngợp. Cụm "ví dụ thực hành" giúp câu trả lời gắn với code, API, token và chi phí thay vì chỉ giải thích lý thuyết.

### Câu 4.2 — Hạn chế & cải thiện
**Trợ lý của bạn hiện có hạn chế lớn nhất là gì (ví dụ: history chỉ 3 lượt,
không có bộ nhớ dài hạn, không kiểm duyệt nội dung...)? Đề xuất một cải
thiện cụ thể và mô tả ngắn cách triển khai:**
> Hạn chế lớn nhất là history chỉ giữ 3 lượt gần nhất, nên trợ lý dễ quên thông tin quan trọng trong cuộc trò chuyện dài. Một cải thiện cụ thể là thêm phần tóm tắt hội thoại: trước khi cắt history, gom các lượt cũ thành một message system hoặc assistant ngắn chứa các ý chính, rồi tiếp tục gửi summary đó cùng 3 lượt gần nhất. Cách này giữ được ngữ cảnh dài hơn mà vẫn kiểm soát chi phí input token.

---

## Danh Sách Kiểm Tra Nộp Bài

- [ ] `python grade.py` — xem điểm tự động, mục tiêu ≥ 75/100
- [ ] Cả 4 checkpoint pytest đều pass
- [ ] Tất cả 9 câu trong file này đã được trả lời
- [ ] Đã copy bài làm vào folder `solution/`, push lên fork và dán link trên trang bài Lab ở VLearn trước 23:59 ngày 11/09/2026
