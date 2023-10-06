package hello;

import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.boot.SpringApplication;

@SpringBootApplication
@RestController
public class Application {

	@RequestMapping("/")
	public String home() {
		return "Hello Docker World";
	}
	@RequestMapping("/hey")
	public String main() {
		var msg = "Hey yo!";
		return msg;
	}

	public static void main(String[] args) {
		SpringApplication.run(Application.class, args);
	}

}
