using System.Globalization;

namespace SmartRouteAI.Backend.Services
{
    public class HolidayService
    {
        private readonly Dictionary<int, List<Holiday>> _holidays;

        public HolidayService()
        {
            _holidays = InitializeHolidays();
        }

        public class Holiday
        {
            public string Name { get; set; } = string.Empty;
            public DateTime Date { get; set; }
            public string Type { get; set; } = string.Empty; // "resmi", "dini", "özel"
            public double TrafficMultiplier { get; set; } = 1.0; // Trafik yoğunluğu çarpanı
        }

        public Holiday? CheckHoliday(DateTime date)
        {
            var year = date.Year;
            if (!_holidays.ContainsKey(year))
            {
                // Eğer yıl için tatil listesi yoksa, sabit tatilleri hesapla
                return CalculateFixedHolidays(date);
            }

            var holiday = _holidays[year].FirstOrDefault(h => h.Date.Date == date.Date);
            if (holiday != null) return holiday;

            // Sabit tatilleri de kontrol et
            return CalculateFixedHolidays(date);
        }

        public bool IsHoliday(DateTime date)
        {
            return CheckHoliday(date) != null;
        }

        public async Task<bool> IsHolidayAsync(DateTime date)
        {
            return await Task.FromResult(IsHoliday(date));
        }
        //Trafik yoğunluğu tahmini
        public double GetTrafficMultiplier(DateTime date)
        {
            var holiday = CheckHoliday(date);
            if (holiday != null)
            {
                return holiday.TrafficMultiplier;
            }

            // Hafta sonu kontrolü
            if (date.DayOfWeek == DayOfWeek.Saturday || date.DayOfWeek == DayOfWeek.Sunday)
            {
                return 1.05; // Hafta sonu trafik yoğunluğu
            }

            return 1.0; // Normal gün
        }

        private Holiday? CalculateFixedHolidays(DateTime date)
        {
            // Sabit tarihli tatiller
            var fixedHolidays = new List<(int month, int day, string name, double multiplier)>
            {
                (1, 1, "Yılbaşı", 1.05),
                (4, 23, "Ulusal Egemenlik ve Çocuk Bayramı", 1.02),
                (5, 1, "Emek ve Dayanışma Günü", 1.05),
                (5, 19, "Atatürk'ü Anma, Gençlik ve Spor Bayramı", 1.02),
                (7, 15, "Demokrasi ve Milli Birlik Günü", 1.02),
                (8, 30, "Zafer Bayramı", 1.02),
                (10, 29, "Cumhuriyet Bayramı", 1.02)
            };

            foreach (var (month, day, name, multiplier) in fixedHolidays)
            {
                if (date.Month == month && date.Day == day)
                {
                    return new Holiday
                    {
                        Name = name,
                        Date = date,
                        Type = "resmi",
                        TrafficMultiplier = multiplier
                    };
                }
            }

            return null;
        }
        //Tatil verileri
        private Dictionary<int, List<Holiday>> InitializeHolidays()
        {
            var holidays = new Dictionary<int, List<Holiday>>();

            // 2024 tatilleri (örnek)
            holidays[2024] = new List<Holiday>
            {
                new Holiday { Name = "Yılbaşı", Date = new DateTime(2024, 1, 1), Type = "resmi", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Ramazan Bayramı", Date = new DateTime(2024, 4, 10), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Ramazan Bayramı", Date = new DateTime(2024, 4, 11), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Ramazan Bayramı", Date = new DateTime(2024, 4, 12), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Ulusal Egemenlik ve Çocuk Bayramı", Date = new DateTime(2024, 4, 23), Type = "resmi", TrafficMultiplier = 1.02 },
                new Holiday { Name = "Emek ve Dayanışma Günü", Date = new DateTime(2024, 5, 1), Type = "resmi", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Atatürk'ü Anma, Gençlik ve Spor Bayramı", Date = new DateTime(2024, 5, 19), Type = "resmi", TrafficMultiplier = 1.02 },
                new Holiday { Name = "Kurban Bayramı", Date = new DateTime(2024, 6, 17), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Kurban Bayramı", Date = new DateTime(2024, 6, 18), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Kurban Bayramı", Date = new DateTime(2024, 6, 19), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Kurban Bayramı", Date = new DateTime(2024, 6, 20), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Demokrasi ve Milli Birlik Günü", Date = new DateTime(2024, 7, 15), Type = "resmi", TrafficMultiplier = 1.02 },
                new Holiday { Name = "Zafer Bayramı", Date = new DateTime(2024, 8, 30), Type = "resmi", TrafficMultiplier = 1.02 },
                new Holiday { Name = "Cumhuriyet Bayramı", Date = new DateTime(2024, 10, 29), Type = "resmi", TrafficMultiplier = 1.02 }
            };

            // 2025 tatilleri (tahmini)
            holidays[2025] = new List<Holiday>
            {
                new Holiday { Name = "Yılbaşı", Date = new DateTime(2025, 1, 1), Type = "resmi", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Ramazan Bayramı", Date = new DateTime(2025, 3, 31), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Ramazan Bayramı", Date = new DateTime(2025, 4, 1), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Ramazan Bayramı", Date = new DateTime(2025, 4, 2), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Ulusal Egemenlik ve Çocuk Bayramı", Date = new DateTime(2025, 4, 23), Type = "resmi", TrafficMultiplier = 1.02 },
                new Holiday { Name = "Emek ve Dayanışma Günü", Date = new DateTime(2025, 5, 1), Type = "resmi", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Atatürk'ü Anma, Gençlik ve Spor Bayramı", Date = new DateTime(2025, 5, 19), Type = "resmi", TrafficMultiplier = 1.02 },
                new Holiday { Name = "Kurban Bayramı", Date = new DateTime(2025, 6, 7), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Kurban Bayramı", Date = new DateTime(2025, 6, 8), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Kurban Bayramı", Date = new DateTime(2025, 6, 9), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Kurban Bayramı", Date = new DateTime(2025, 6, 10), Type = "dini", TrafficMultiplier = 1.05 },
                new Holiday { Name = "Demokrasi ve Milli Birlik Günü", Date = new DateTime(2025, 7, 15), Type = "resmi", TrafficMultiplier = 1.02 },
                new Holiday { Name = "Zafer Bayramı", Date = new DateTime(2025, 8, 30), Type = "resmi", TrafficMultiplier = 1.02 },
                new Holiday { Name = "Cumhuriyet Bayramı", Date = new DateTime(2025, 10, 29), Type = "resmi", TrafficMultiplier = 1.02 }
            };

            return holidays;
        }
        //Tatilin trafik etkisi
        public string GetHolidayImpact(DateTime date)
        {
            var holiday = CheckHoliday(date);
            if (holiday == null) return "Tatil günü değil";

            var impact = holiday.TrafficMultiplier switch
            {
                >= 1.05 => "Hafif artış bekleniyor",
                >= 1.02 => "Minimal artış bekleniyor",
                _ => "Normal trafik yoğunluğu"
            };

            return $"{holiday.Name} - {impact}";
        }
    }
} 