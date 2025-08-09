package com.example.demo.service;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import com.example.demo.dto.OrderDto;
import com.example.demo.entity.OrderEntity;
import com.example.demo.repository.OrderRepository;
import static org.assertj.core.api.Assertions.*;

@SpringBootTest
public class OrderServiceTest {

    @Autowired
    private OrderService orderService;

    @Autowired
    private OrderRepository orderRepository;

    @Test
    public void createOrder_shouldSaveOrderInDatabase() {
        // given
        OrderDto orderDto = new OrderDto();
        orderDto.setCustomerName("John Doe");
        orderDto.setTotalAmount(100.0);

        // when
        orderService.createOrder(orderDto);

        // then
        assertThat(orderRepository.findAll()).hasSize(1);
    }

}
```

Note that the above code is just a sample and may need to be modified based on specific requirements. Additionally, this code assumes that the database is PostgreSQL, but if the SQL logic clearly targets another DB, you should adjust the code accordingly.


Here are the files for the given project: